import unittest

from auth_checker import check_domain, dict_resolver


def base_zone(**overrides):
    zone = {
        "d.com": ["v=spf1 include:a.net ~all"],
        "a.net": ["v=spf1 ip4:1.2.3.0/24 ~all"],
        "_dmarc.d.com": ["v=DMARC1; p=quarantine; rua=mailto:r@d.com"],
    }
    zone.update(overrides)
    return zone


class SpfTests(unittest.TestCase):
    def test_clean_domain_passes(self):
        r = check_domain("D.com", dict_resolver(base_zone()))
        self.assertTrue(r.ok, r.errors)
        self.assertIn("SPF DNS lookups: 1/10", r.info)

    def test_missing_spf(self):
        r = check_domain("d.com", dict_resolver(base_zone(**{"d.com": ["some-other-txt"]})))
        self.assertTrue(any("No SPF record" in e for e in r.errors))

    def test_two_spf_records_is_error(self):
        r = check_domain("d.com", dict_resolver(base_zone(**{"d.com": ["v=spf1 -all", "v=spf1 ~all"]})))
        self.assertTrue(any("2 SPF records" in e for e in r.errors))

    def test_lookup_limit_counts_nested_includes(self):
        zone = base_zone(**{"d.com": ["v=spf1 " + " ".join(f"include:s{i}.net" for i in range(6)) + " ~all"]})
        for i in range(6):
            zone[f"s{i}.net"] = [f"v=spf1 include:t{i}.net ~all"]
            zone[f"t{i}.net"] = ["v=spf1 ip4:10.0.0.0/8 ~all"]
        r = check_domain("d.com", dict_resolver(zone))
        self.assertTrue(any("12 DNS lookups" in e for e in r.errors))

    def test_near_limit_warning(self):
        zone = base_zone(**{"d.com": ["v=spf1 a mx " + " ".join(f"include:s{i}.net" for i in range(6)) + " -all"]})
        for i in range(6):
            zone[f"s{i}.net"] = ["v=spf1 ip4:10.0.0.0/8 -all"]
        r = check_domain("d.com", dict_resolver(zone))
        self.assertTrue(r.ok)
        self.assertTrue(any("8/10" in w for w in r.warnings))

    def test_plus_all_is_error(self):
        r = check_domain("d.com", dict_resolver(base_zone(**{"d.com": ["v=spf1 +all"]})))
        self.assertTrue(any("+all" in e for e in r.errors))

    def test_missing_include_target_and_loop(self):
        missing = check_domain("d.com", dict_resolver(base_zone(**{"a.net": []})))
        self.assertTrue(any("a.net has no SPF record" in e for e in missing.errors))
        loop = check_domain("d.com", dict_resolver(base_zone(**{"a.net": ["v=spf1 include:d.com ~all"]})))
        self.assertTrue(any("loop" in e for e in loop.errors))


class DmarcTests(unittest.TestCase):
    def test_missing_dmarc_is_error(self):
        zone = base_zone()
        del zone["_dmarc.d.com"]
        r = check_domain("d.com", dict_resolver(zone))
        self.assertTrue(any("No DMARC" in e for e in r.errors))

    def test_p_none_warns_but_passes(self):
        r = check_domain("d.com", dict_resolver(base_zone(**{"_dmarc.d.com": ["v=DMARC1; p=none; rua=mailto:x@d.com"]})))
        self.assertTrue(r.ok)
        self.assertTrue(any("p=none" in w for w in r.warnings))

    def test_no_rua_and_pct(self):
        r = check_domain("d.com", dict_resolver(base_zone(**{"_dmarc.d.com": ["v=DMARC1; p=reject; pct=25"]})))
        self.assertTrue(any("rua" in w for w in r.warnings))
        self.assertTrue(any("pct=25" in w for w in r.warnings))

    def test_invalid_policy(self):
        r = check_domain("d.com", dict_resolver(base_zone(**{"_dmarc.d.com": ["v=DMARC1; rua=mailto:x@d.com"]})))
        self.assertTrue(any("policy" in e for e in r.errors))


if __name__ == "__main__":
    unittest.main()
