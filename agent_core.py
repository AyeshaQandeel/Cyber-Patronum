import html
import ipaddress
import math
import re
import socket
import ssl
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

# ----------------------------------------------------------------------------
# Knowledge tables used by the heuristics
# ----------------------------------------------------------------------------
SUSPICIOUS_TLDS = {
    "zip", "mov", "top", "xyz", "click", "work", "gq", "tk", "ml", "ga", "cf",
    "icu", "buzz", "cyou", "monster", "loan", "men", "rest", "country", "kim",
    "support", "download", "review", "stream", "science", "party", "bid",
}
PHISH_KEYWORDS = [
    "login", "signin", "verify", "secure", "account", "update", "wallet",
    "banking", "billing", "support", "password", "confirm", "unlock",
    "recover", "suspend",
]
BRANDS = [
    "paypal", "google", "microsoft", "apple", "amazon", "facebook", "instagram",
    "netflix", "binance", "coinbase", "whatsapp", "linkedin", "github",
    "dropbox", "office365", "outlook", "icloud", "metamask",
]
KNOWN_LEGIT = {
    "google-analytics.com", "amazon-adsystem.com", "apple-dns.net",
    "googletagmanager.com",
}
REPUTABLE_ORGS = [
    "google", "cloudflare", "amazon", "microsoft", "akamai", "fastly",
    "github", "apple inc", "facebook", "meta platforms", "automattic",
    "wikimedia",
]
VPS_KEYWORDS = [
    "digitalocean", "linode", "vultr", "hetzner", "contabo", "ovh",
    "leaseweb", "choopa", "frantech", "hostinger", "namecheap", "godaddy",
]
VPN_PATTERNS = [r"m247", r"vpn", r"\btor\b", r"proxy", r"bulletproof", r"anonymi"]
HIGH_ACTIVITY_COUNTRIES = {"Russia", "China", "Romania", "Seychelles"}
SECURITY_HEADERS = [
    "strict-transport-security", "content-security-policy", "x-frame-options",
    "x-content-type-options", "referrer-policy", "permissions-policy",
]
DNSBL_ZONES = [
    ("Spamhaus ZEN", "zen.spamhaus.org"),
    ("SpamCop", "bl.spamcop.net"),
    ("DroneBL", "dnsbl.dronebl.org"),
]
DNS_TYPES = {"A": 1, "NS": 2, "CNAME": 5, "PTR": 12, "MX": 15, "TXT": 16, "AAAA": 28, "CAA": 257}
BASELINE = 10  # neutral starting score; every finding moves it up or down


def _fmt_pts(p: int) -> str:
    if p > 0:
        return f"+{p}"
    if p < 0:
        return f"\u2212{abs(p)}"
    return "\u00b10"


class CyberPatronumAgent:
    """
    Cyber-Patronum — Magical Cybersecurity Investigation Agent
    Open Agent Hackathon 2026 | Track 2: The Agent That Can Explain Why

    Accepts domains, subdomains, full URLs, IPv4 and IPv6 addresses.
    Every score is the sum of explicit, named signals, so the report can
    explain exactly why a target got its score.
    """

    def __init__(self, target: str):
        self.raw_target = target or ""
        self.target = self._normalize(self.raw_target)
        self.is_ip = self._is_ip(self.target)
        self.lookup_name = self._to_ascii(self.target)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Cyber-Patronum/2.0 (OSINT research agent)"})
        self._signals: Optional[List[Dict[str, Any]]] = None
        self._floor_applied = False

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
    @staticmethod
    def _is_ip(value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    @classmethod
    def _normalize(cls, raw: str) -> str:
        t = raw.strip()
        if cls._is_ip(t):
            return t
        parsed = urlparse(t if "://" in t else "//" + t)
        try:
            host = parsed.hostname or t
        except ValueError:
            host = t
        return host.strip().strip(".").lower()

    @staticmethod
    def _to_ascii(host: str) -> str:
        try:
            return host.encode("idna").decode("ascii")
        except Exception:
            return host

    def _valid_hostname(self) -> bool:
        pattern = r"^(?=.{1,253}$)([a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?\.)+[a-z0-9-]{2,63}$"
        return bool(re.match(pattern, self.lookup_name))

    @staticmethod
    def _registrable(host: str) -> str:
        labels = host.split(".")
        if len(labels) <= 2:
            return host
        if len(labels[-1]) == 2 and labels[-2] in {"co", "com", "org", "net", "gov", "edu", "ac", "or", "ne", "go"}:
            return ".".join(labels[-3:])
        return ".".join(labels[-2:])

    @staticmethod
    def _entropy(s: str) -> float:
        if not s:
            return 0.0
        n = len(s)
        return -sum(c / n * math.log2(c / n) for c in Counter(s).values())

    # ------------------------------------------------------------------
    # Data collection (all free, keyless public endpoints)
    # ------------------------------------------------------------------
    def _empty_record(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "ip": None,
            "ips": [],
            "country": "Unknown",
            "country_code": "",
            "region": "",
            "city": "",
            "asn": "Unknown ASN",
            "asname": "",
            "org": "Unknown Org",
            "isp": "",
            "is_ip": self.is_ip,
            "is_proxy": False,
            "is_hosting": False,
            "is_mobile": False,
            "reverse_dns": None,
            "dns": {"a": [], "aaaa": [], "mx": [], "ns": [], "txt": [], "caa": [], "dmarc": [], "nxdomain": False},
            "rdap": {"answered": False, "created": None, "age_days": None, "registrar": None},
            "tls": None,
            "http": None,
            "blocklists": {"checked": 0, "listed": []},
            "sources": {},
            "errors": [],
            "live_status": "Success",
            "public_ip": None,
            "redirect_probe": None,
        }

    def _doh(self, name: str, rtype: str, timeout: int = 4) -> Dict[str, Any]:
        res = {"ok": False, "status": None, "answers": []}
        try:
            r = self.session.get(
                "https://dns.google/resolve",
                params={"name": name, "type": rtype},
                timeout=timeout,
            )
            j = r.json()
            want = DNS_TYPES[rtype]
            res["ok"] = True
            res["status"] = j.get("Status")
            res["answers"] = [a.get("data", "") for a in j.get("Answer", []) if a.get("type") == want]
        except Exception:
            pass
        return res

    def _rdap(self, name: str) -> Dict[str, Any]:
        out = {"answered": False, "created": None, "age_days": None, "registrar": None}
        labels = name.split(".")
        candidates = [".".join(labels[i:]) for i in range(0, max(1, len(labels) - 1))][:3]
        for cand in candidates:
            try:
                r = self.session.get(
                    f"https://rdap.org/domain/{cand}",
                    headers={"Accept": "application/rdap+json"},
                    timeout=5,
                )
            except requests.RequestException:
                continue
            if r.status_code == 404:
                out["answered"] = True
                continue
            if r.status_code != 200:
                continue
            try:
                j = r.json()
                out["answered"] = True
                for e in j.get("events", []):
                    if e.get("eventAction") == "registration":
                        created = datetime.fromisoformat(e["eventDate"].replace("Z", "+00:00"))
                        if created.tzinfo is None:
                            created = created.replace(tzinfo=timezone.utc)
                        out["created"] = created.date().isoformat()
                        out["age_days"] = max(0, (datetime.now(timezone.utc) - created).days)
                        break
                for ent in j.get("entities", []):
                    if "registrar" in ent.get("roles", []):
                        for item in ent.get("vcardArray", [None, []])[1]:
                            if item and item[0] == "fn":
                                out["registrar"] = item[3]
            except Exception:
                pass
            break
        return out

    def _ipinfo(self, ip: str) -> Dict[str, Any]:
        try:
            r = self.session.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,message,country,countryCode,regionName,city,isp,org,as,asname,reverse,mobile,proxy,hosting"},
                timeout=5,
            )
            j = r.json()
            if j.get("status") == "success":
                j["ok"] = True
                return j
        except Exception:
            pass
        return {"ok": False}

    def _blocklists(self, ip: str) -> Dict[str, Any]:
        out = {"checked": 0, "listed": []}
        rev = ".".join(reversed(ip.split(".")))
        for label, zone in DNSBL_ZONES:
            res = self._doh(f"{rev}.{zone}", "A")
            if not res["ok"]:
                continue
            # 127.255.255.x are "public resolver / query refused" codes, not listings
            real = [a for a in res["answers"] if a.startswith("127.") and not a.startswith("127.255.255.")]
            out["checked"] += 1
            if real:
                out["listed"].append(label)
        return out

    def _tls(self, host: str) -> Dict[str, Any]:
        out = {"answered": False, "https": False, "valid": None, "issuer": None,
               "subject": None, "days_left": None, "error": None}
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ss:
                    cert = ss.getpeercert()
                    out.update(answered=True, https=True, valid=True)
                    issuer = dict(x[0] for x in cert.get("issuer", ()))
                    subject = dict(x[0] for x in cert.get("subject", ()))
                    out["issuer"] = issuer.get("organizationName") or issuer.get("commonName")
                    out["subject"] = subject.get("commonName")
                    exp = ssl.cert_time_to_seconds(cert["notAfter"])
                    out["days_left"] = int((exp - time.time()) / 86400)
        except ssl.SSLCertVerificationError as e:
            out.update(answered=True, https=True, valid=False, error=getattr(e, "verify_message", None) or str(e))
        except ssl.SSLError as e:
            out.update(answered=True, https=True, valid=None, error=str(e))
        except ConnectionRefusedError:
            out.update(answered=True, https=False)
        except OSError:
            pass  # timeout / unreachable: leave answered=False
        return out

    def _http(self, host: str) -> Dict[str, Any]:
        out = {"answered": False, "status": None, "final_host": None, "redirects": 0,
               "cross_domain": False, "server": None, "security_headers": [], "scheme": None}
        hostpart = f"[{host}]" if ":" in host else host
        for scheme in ("https", "http"):
            try:
                r = self.session.get(f"{scheme}://{hostpart}", timeout=6, allow_redirects=True, stream=True)
            except requests.exceptions.TooManyRedirects:
                out.update(answered=True, redirects=30)
                break
            except requests.RequestException:
                continue
            try:
                final_host = urlparse(r.url).hostname or host
                headers = {k.lower() for k in r.headers}
                out.update(
                    answered=True,
                    status=r.status_code,
                    scheme=scheme,
                    final_host=final_host,
                    redirects=len(r.history),
                    server=r.headers.get("Server"),
                    security_headers=[h for h in SECURITY_HEADERS if h in headers],
                )
                if self._is_ip(host):
                    out["cross_domain"] = final_host != host
                else:
                    out["cross_domain"] = self._registrable(final_host) != self._registrable(host)
            finally:
                r.close()
            break
        return out

    def fetch_live_dns_ip_data(self) -> Dict[str, Any]:
        """Collects live telemetry for any domain, URL, or IP address."""
        d = self._empty_record()
        if not (self.is_ip or self._valid_hostname()):
            d["live_status"] = "Invalid"
            d["errors"].append("Input is not a valid domain name or IP address.")
            return d

        name = self.lookup_name
        with ThreadPoolExecutor(max_workers=10) as pool:
            rdap_future = None
            if self.is_ip:
                d["ip"] = self.target
                d["ips"] = [self.target]
            else:
                jobs = {t: pool.submit(self._doh, name, t) for t in ("A", "AAAA", "MX", "NS", "TXT", "CAA")}
                jobs["DMARC"] = pool.submit(self._doh, "_dmarc." + name, "TXT")
                rdap_future = pool.submit(self._rdap, name)
                res = {k: f.result() for k, f in jobs.items()}

                clean = lambda xs: [x.replace('" "', "").strip('"') for x in xs]
                a = [x for x in res["A"]["answers"] if self._is_ip(x)]
                aaaa = [x for x in res["AAAA"]["answers"] if self._is_ip(x)]
                d["dns"] = {
                    "a": a, "aaaa": aaaa,
                    "mx": res["MX"]["answers"], "ns": res["NS"]["answers"],
                    "txt": clean(res["TXT"]["answers"]), "caa": res["CAA"]["answers"],
                    "dmarc": clean(res["DMARC"]["answers"]),
                    "nxdomain": res["A"]["status"] == 3,
                }
                d["sources"]["dns"] = res["A"]["ok"]
                if not res["A"]["ok"]:
                    d["errors"].append("DNS-over-HTTPS lookup failed.")
                d["ips"] = a + aaaa
                d["ip"] = d["ips"][0] if d["ips"] else None

            # ---- stage 2: everything that needs the resolved IP ----
            futs = {}
            ip = d["ip"]
            if ip:
                ipobj = ipaddress.ip_address(ip)
                d["public_ip"] = ipobj.is_global
                if ipobj.is_global:
                    futs["ipinfo"] = pool.submit(self._ipinfo, ip)
                    futs["rdns"] = pool.submit(self._doh, ipobj.reverse_pointer, "PTR")
                    if ipobj.version == 4:
                        futs["bl"] = pool.submit(self._blocklists, ip)
                    futs["http"] = pool.submit(self._http, name)
                    if not self.is_ip:
                        futs["tls"] = pool.submit(self._tls, name)

            if rdap_future is not None:
                d["rdap"] = rdap_future.result()
                d["sources"]["rdap"] = d["rdap"]["answered"]
                if not d["rdap"]["answered"]:
                    d["errors"].append("Domain registration data (RDAP) was unavailable.")

            if "ipinfo" in futs:
                info = futs["ipinfo"].result()
                d["sources"]["ipinfo"] = info["ok"]
                if info["ok"]:
                    d["country"] = info.get("country") or "Unknown"
                    d["country_code"] = info.get("countryCode", "")
                    d["region"] = info.get("regionName", "")
                    d["city"] = info.get("city", "")
                    d["org"] = info.get("org") or info.get("isp") or "Unknown Org"
                    d["isp"] = info.get("isp", "")
                    d["asn"] = info.get("as") or "Unknown ASN"
                    d["asname"] = info.get("asname", "")
                    d["is_proxy"] = bool(info.get("proxy"))
                    d["is_hosting"] = bool(info.get("hosting"))
                    d["is_mobile"] = bool(info.get("mobile"))
                else:
                    d["errors"].append("IP intelligence service (ip-api) was unreachable or rate-limited.")
            if "rdns" in futs:
                r = futs["rdns"].result()
                d["sources"]["rdns"] = r["ok"]
                if r["answers"]:
                    d["reverse_dns"] = r["answers"][0].rstrip(".")
            if "bl" in futs:
                d["blocklists"] = futs["bl"].result()
                d["sources"]["blocklist"] = d["blocklists"]["checked"] > 0
                if d["blocklists"]["checked"] == 0:
                    d["errors"].append("Reputation blocklists could not be queried.")
            if "tls" in futs:
                d["tls"] = futs["tls"].result()
                d["sources"]["tls"] = d["tls"]["answered"]
            if "http" in futs:
                d["http"] = futs["http"].result()
                d["sources"]["http"] = d["http"]["answered"]

        if d["errors"]:
            d["live_status"] = "Partial"
        return d

    # ------------------------------------------------------------------
    # Heuristic analysis: every finding is a named signal with points
    # ------------------------------------------------------------------
    def _analyze(self, d: Dict[str, Any]) -> List[Dict[str, Any]]:
        S: List[Dict[str, Any]] = []

        def add(points: int, title: str, detail: str, tag: Optional[str] = None):
            if points >= 10:
                sev = "bad"
            elif points > 0:
                sev = "warn"
            elif points < 0:
                sev = "good"
            else:
                sev = "info"
            S.append({"severity": sev, "points": points, "title": title, "detail": detail, "tag": tag})

        blob = f"{d['org']} {d['isp']} {d['asn']} {d['asname']}".lower()
        reputable = any(k in blob for k in REPUTABLE_ORGS)

        # ---------- domain-only checks ----------
        if not self.is_ip:
            host = self.lookup_name
            reg = self._registrable(host)
            sld = reg.split(".")[0]
            tld = host.rsplit(".", 1)[-1]

            if "xn--" in host:
                add(12, "Punycode / look-alike characters",
                    "The name uses internationalised characters, a common trick for impersonating real brands.")
            if tld in SUSPICIOUS_TLDS:
                add(8, f"High-abuse TLD (.{tld})",
                    "This top-level domain is cheap or free and heavily used in abuse campaigns.")

            hits = [k for k in PHISH_KEYWORDS if k in sld]
            if hits:
                add(12 if len(hits) >= 2 else 6, "Credential-bait wording in the name",
                    f"The domain contains words attackers like to use: {', '.join(hits)}.")

            leet = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t"})
            norm = sld.translate(leet)
            if reg not in KNOWN_LEGIT:
                for brand in BRANDS:
                    if brand in norm and sld != brand and (norm != sld or "-" in sld):
                        add(10, f"Possible '{brand}' look-alike",
                            f"'{sld}' resembles the brand '{brand}' but is not its real domain.")
                        break

            if sld.count("-") >= 3:
                add(4, "Many hyphens in the name", "Long hyphenated names are typical of throwaway domains.")
            if len(sld) >= 6 and sum(c.isdigit() for c in sld) / len(sld) > 0.3:
                add(4, "Digit-heavy name", "A high share of digits is typical of generated domains.")
            if len(sld) >= 12 and self._entropy(sld) > 3.4:
                add(6, "Random-looking name", "High character randomness suggests an algorithmically generated domain.")
            if host.count(".") >= 4:
                add(3, "Deeply nested subdomains", "Very long subdomain chains are often used to hide the real domain.")

            dns = d["dns"]
            if dns["nxdomain"]:
                add(0, "Domain does not resolve",
                    "DNS reports NXDOMAIN, so there is no live host to investigate (it may be parked, expired, or mistyped).")
            elif d["sources"].get("dns") and not d["ips"]:
                add(0, "No address records", "The name exists but has no A/AAAA record.")

            rd = d["rdap"]
            if rd["age_days"] is not None:
                days = rd["age_days"]
                if days < 30:
                    add(25, "Newly registered domain", f"Registered only {days} day(s) ago ({rd['created']}); most phishing domains are this young.")
                elif days < 90:
                    add(15, "Very young domain", f"Registered {days} days ago ({rd['created']}).")
                elif days < 365:
                    add(6, "Young domain", f"Registered {days} days ago ({rd['created']}).")
                elif days >= 1095:
                    add(-5, "Established domain", f"Registered {days // 365} year(s) ago ({rd['created']}).")
            elif rd["answered"]:
                add(0, "Domain age unknown", "The registry did not publish a creation date.")

            if dns["mx"]:
                has_spf = any(t.lower().startswith("v=spf1") for t in dns["txt"])
                has_dmarc = any(t.lower().startswith("v=dmarc1") for t in dns["dmarc"])
                if not has_spf and not has_dmarc:
                    add(4, "Mail setup is spoofable", "The domain handles email but publishes neither SPF nor DMARC.")

        # ---------- IP-level checks ----------
        ip = d["ip"]
        if ip and d["public_ip"] is False:
            if self.is_ip:
                add(0, "Private or reserved address", "This is not a public internet address, so no external telemetry exists for it.")
            else:
                add(15, "Resolves to a non-public address",
                    f"The domain points to {ip}, an internal or reserved range (sinkhole, misconfiguration, or DNS-rebinding setup).")
        elif ip:
            vpn_hit = any(re.search(p, blob) for p in VPN_PATTERNS)
            vps_hit = any(k in blob for k in VPS_KEYWORDS)
            if d["is_proxy"]:
                add(22, "Known proxy / VPN / Tor exit",
                    f"The IP intelligence feed marks {ip} as an anonymising proxy ({d['org']}).")
            elif vpn_hit:
                add(10, "Anonymity-service network", f"The network name suggests a VPN or proxy provider ({d['org']}).")
            elif (d["is_hosting"] or vps_hit) and not reputable:
                add(5 if vps_hit else 3, "Commodity hosting / VPS",
                    f"Hosted on rented server infrastructure ({d['org']}); common for both small sites and throwaway attack servers.")

            if d["country"] in HIGH_ACTIVITY_COUNTRIES:
                add(5, f"High-activity hosting region ({d['country']})",
                    "A weak signal on its own; geography alone is never proof of malice.", tag="FORBIDDEN JURISDICTION")

            bl = d["blocklists"]
            if bl["listed"]:
                pts = min(55, 35 + 10 * (len(bl["listed"]) - 1))
                add(pts, "Listed on reputation blocklists", f"Flagged by: {', '.join(bl['listed'])}.")
            elif bl["checked"]:
                add(-3, "Clean on blocklists", f"Not listed on {bl['checked']} public reputation list(s) (best effort).")

        # ---------- probes ----------
        tls = d["tls"]
        if tls and tls["answered"]:
            if not tls["https"]:
                add(5, "No HTTPS service", "Port 443 refused the connection; the site cannot offer an encrypted session.")
            elif tls["valid"] is False:
                add(20, "Certificate fails validation", f"The TLS certificate was rejected: {tls['error']}.")
            elif tls["valid"]:
                add(-3, "Valid TLS certificate", f"Issued by {tls['issuer'] or 'unknown CA'}, {tls['days_left']} day(s) remaining.")
                if tls["days_left"] is not None and tls["days_left"] <= 7:
                    add(3, "Certificate expires very soon", f"Only {tls['days_left']} day(s) left.")

        http = d["http"]
        if http and http["answered"]:
            if http["redirects"] >= 30:
                add(6, "Redirect loop", "The site redirects endlessly, a trait of cloaking or broken infrastructure.")
            else:
                if http["cross_domain"]:
                    add(6, "Redirects to another domain", f"Visitors end up on {http['final_host']}.")
                if http["redirects"] > 4:
                    add(4, "Long redirect chain", f"{http['redirects']} hops before the final page.")
                if len(http["security_headers"]) >= 3:
                    add(-3, "Hardened web server", f"Sends {len(http['security_headers'])} of {len(SECURITY_HEADERS)} standard security headers.")

        rp = d.get("redirect_probe")
        if rp and rp.get("age_days") is not None:
            if rp["age_days"] < 90:
                add(12, "Redirect destination is a young domain",
                    f"{rp['host']} was registered only {rp['age_days']} day(s) ago.")
            elif rp["age_days"] >= 730:
                add(-2, "Redirect destination is established",
                    f"{rp['host']} is about {rp['age_days'] // 365} year(s) old.")

        return S

    def _score(self, signals: List[Dict[str, Any]]) -> int:
        total = BASELINE + sum(s["points"] for s in signals)
        # A serious finding can't be averaged away by minor good signals.
        floor = 20 if any(s["severity"] == "bad" for s in signals) else 1
        self._floor_applied = floor == 20 and total < 20
        return int(max(floor, min(99, total)))

    @staticmethod
    def _verdict(score: int) -> str:
        if score < 20:
            return "LOW RISK // WARD HOLDS"
        if score < 45:
            return "MODERATE // STAY ALERT"
        if score < 70:
            return "ELEVATED // DARK ARTS SUSPECTED"
        return "HIGH // DARK MARK DETECTED"

    def run_heuristic_checks(self, data: Dict[str, Any]) -> List[str]:
        """Analyzes real-time evidence and returns human-readable flags."""
        if data.get("live_status") == "Invalid":
            self._signals = []
            return ["CURSE WARNING: That input is not a valid domain name, URL, or IP address."]

        self._signals = self._analyze(data)
        prefix = {"bad": "DARK ARTS ANOMALY", "warn": "CURSE WARNING", "good": "PATRONUM WARD HOLDS", "info": "SCRYING NOTE"}
        order = {"bad": 0, "warn": 1, "good": 2, "info": 3}

        flags = []
        if not any(s["severity"] in ("bad", "warn") for s in self._signals):
            if self._confidence(data) != "Low":
                flags.append("PATRONUM WARD CLEAN: No dark magic or high-risk anomalies found")
            elif not self._signals:
                flags.append("SCRYING NOTE: Too little telemetry to judge this target (inconclusive, not clean)")
        for s in sorted(self._signals, key=lambda s: (order[s["severity"]], -abs(s["points"]))):
            if s["severity"] == "info" and len(self._signals) > 1:
                continue
            tag = s["tag"] or prefix[s["severity"]]
            pts = "" if s["points"] == 0 else f" ({_fmt_pts(s['points'])})"
            flags.append(f"{tag}: {s['title']}{pts}")
        return flags[:8]

    # ------------------------------------------------------------------
    # Track 2: explain why
    # ------------------------------------------------------------------
    @staticmethod
    def _domain_age_text(d: Dict[str, Any]) -> str:
        days = d["rdap"]["age_days"]
        if d["is_ip"]:
            return "N/A (IP address)"
        if days is None:
            return "Unknown"
        if days < 60:
            return f"{days} day(s)"
        if days < 730:
            return f"{days // 30} month(s)"
        return f"{days // 365} year(s)"

    @staticmethod
    def _tls_text(d: Dict[str, Any]) -> str:
        t = d["tls"]
        if d["is_ip"]:
            return "N/A (IP address)"
        if not t or not t["answered"]:
            return "Not checked"
        if not t["https"]:
            return "No HTTPS"
        if t["valid"] is False:
            return "INVALID CERTIFICATE"
        if t["valid"]:
            return f"Valid, {t['days_left']}d left"
        return "Handshake problem"

    def _confidence(self, d: Dict[str, Any]) -> str:
        src = d["sources"]
        if not src or not d["ip"]:
            return "Low"
        ratio = sum(1 for v in src.values() if v) / len(src)
        if ratio >= 0.8:
            return "High"
        if ratio >= 0.5:
            return "Medium"
        return "Low"

    def generate_explanation(self, data: Dict[str, Any], flags: List[str]) -> Dict[str, Any]:
        """Builds the score, a short reasoning summary, and a full evidence scroll."""
        if self._signals is None:
            self._signals = self._analyze(data) if data.get("live_status") != "Invalid" else []
        sigs = self._signals
        esc = html.escape
        details = ""

        if data.get("live_status") == "Invalid":
            score, confidence, verdict = 0, "Low", "INVALID TARGET"
            explanation = (
                f"<b>{esc(self.raw_target[:80])}</b> is not a valid domain, URL, or IP address. "
                "Try <b>example.com</b>, <b>https://example.com/page</b>, or <b>8.8.8.8</b>."
            )
        else:
            score = self._score(sigs)
            confidence = self._confidence(data)
            verdict = self._verdict(score)
            if data["ip"] and data["public_ip"] is False and self.is_ip:
                verdict = "PRIVATE ADDRESS // NO PUBLIC DATA"
            elif confidence == "Low" and score < 20:
                verdict = "INCONCLUSIVE // TOO LITTLE EVIDENCE"

            up = sorted([s for s in sigs if s["points"] > 0], key=lambda s: -s["points"])
            down = sorted([s for s in sigs if s["points"] < 0], key=lambda s: s["points"])
            notes = [s for s in sigs if s["points"] == 0]

            def short(s, with_detail):
                txt = f"\u2022 <b>{_fmt_pts(s['points'])}</b> {esc(s['title'])}"
                return txt + (f" \u2014 {esc(s['detail'])}" if with_detail else "")

            known_org = data["org"] not in ("Unknown Org", "") and data["country"] != "Unknown"
            parts = [f"<b>{esc(self.target)}</b> scores <b>{score}%</b> risk at <b>{confidence}</b> confidence."
                     + (f" It resolves to {esc(data['ip'])} ({esc(data['org'])}, {esc(data['country'])})."
                        if known_org and not self.is_ip else "")]
            if up:
                parts.append("<b>Why it rises:</b><br>" + "<br>".join(short(s, True) for s in up[:3])
                             + (f"<br>\u2022 \u2026and {len(up) - 3} more" if len(up) > 3 else ""))
            if down:
                parts.append("<b>What lowers it:</b><br>" + "<br>".join(short(s, False) for s in down[:3]))
            if not up and not down:
                parts.append(" ".join(esc(s["detail"]) for s in notes[:2]) or "No signals moved the score from its baseline.")
            explanation = "<br><br>".join(parts)

            # ---- full evidence scroll (shown in an expander) ----
            rows = [f"Baseline: {BASELINE}%"]
            for s in sorted(sigs, key=lambda s: -s["points"]):
                rows.append(f"\u2022 <b>{_fmt_pts(s['points'])}</b> {esc(s['title'])} \u2014 {esc(s['detail'])}")
            if self._floor_applied:
                rows.append("\u2022 <b>Minimum 20%</b> A serious finding sets a floor, so minor good signals cannot push the score into the low band.")
            blind = list(data["errors"])
            labels = {"tls": "TLS certificate check", "http": "web server probe", "rdns": "reverse DNS lookup"}
            for k, v in data["sources"].items():
                if not v and k in labels:
                    blind.append(f"The {labels[k]} timed out.")
            if data["ip"] and data["public_ip"] is False:
                blind.append("Active probes were skipped because the address is not public.")
            blocks = ["<b>Every signal behind the score</b><br>" + "<br>".join(rows)]
            if blind:
                blocks.append("<b>Blind spots</b><br>" + "<br>".join("\u2022 " + esc(b) for b in blind))
            blocks.append("<i>A heuristic read of public OSINT signals, not a guarantee. A low score does not prove "
                          "a site is safe, and a high score does not prove it is malicious.</i>")
            details = "<br><br>".join(blocks)

        return {
            "target": self.target,
            "ip": data.get("ip"),
            "country": data.get("country"),
            "org": data.get("org"),
            "asn": data.get("asn"),
            "reverse_dns": data.get("reverse_dns") or "None published",
            "domain_age": self._domain_age_text(data),
            "tls_summary": self._tls_text(data),
            "risk_score": score,
            "confidence": confidence,
            "verdict": verdict,
            "flags": flags,
            "signals": sigs,
            "explanation": explanation,
            "details": details,
        }