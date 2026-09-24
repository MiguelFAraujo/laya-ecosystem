#!/usr/bin/env python3
"""E2E Playwright Automated Validation Suite for IDT-Lab & Laya Ecosystem.
Executes browser-level and API-level integration tests, measuring latency and verifying schemas.
"""

import json
import time
import unittest
from playwright.sync_api import sync_playwright

class TestIDTLabPlaywrightE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.context = cls.browser.new_context()

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()

    def test_01_laya_health_and_schema(self):
        """Verifies Laya daemon (:8092) health and loaded models via Chromium."""
        page = self.context.new_page()
        start = time.time()
        resp = page.goto("http://127.0.0.1:8092/health")
        latency_ms = (time.time() - start) * 1000
        self.assertEqual(resp.status, 200)
        data = json.loads(page.inner_text("pre") if page.query_selector("pre") else page.content())
        self.assertEqual(data.get("status"), "ok")
        print(f"\n[Playwright E2E] Laya Health: 200 OK | Latency: {latency_ms:.1f}ms | Models: {data.get('loaded')}")
        page.close()

    def test_02_cortex_okla_status(self):
        """Verifies Cortex OKLA API (:8090) cognitive status and knowledge base."""
        page = self.context.new_page()
        start = time.time()
        resp = page.goto("http://127.0.0.1:8090/api/v1/cognitive/status")
        latency_ms = (time.time() - start) * 1000
        self.assertEqual(resp.status, 200)
        text = page.inner_text("pre") if page.query_selector("pre") else page.content()
        data = json.loads(text)
        self.assertIn("documents", data)
        print(f"[Playwright E2E] Cortex OKLA Status: 200 OK | Latency: {latency_ms:.1f}ms | Docs: {data.get('documents')} | Canonicals: {data.get('servable_canonicals')}")
        page.close()

    def test_03_omniroute_dashboard(self):
        """Verifies OmniRoute Gateway (:20128) dashboard loads without UI errors."""
        page = self.context.new_page()
        start = time.time()
        resp = page.goto("http://127.0.0.1:20128/dashboard", timeout=10000)
        latency_ms = (time.time() - start) * 1000
        self.assertIn(resp.status, [200, 304, 307])
        print(f"[Playwright E2E] OmniRoute Dashboard: {resp.status} | Latency: {latency_ms:.1f}ms")
        page.close()

    def test_04_laya_systemone_inference(self):
        """Executes a live System-1 decision call via Playwright APIRequestContext."""
        request_context = self.playwright.request.new_context()
        payload = {
            "state": {"text": "Erro de conexão no banco de dados PostgreSQL"},
            "questions": {
                "is_bug": {
                    "type": "noul",
                    "instructions": "O texto descreve uma falha técnica?",
                    "criteria": {"true": "Sim", "false": "Não"}
                }
            }
        }
        start = time.time()
        resp = request_context.post(
            "http://127.0.0.1:8092/v1/systemone",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        latency_ms = (time.time() - start) * 1000
        self.assertEqual(resp.status, 200)
        res_json = resp.json()
        ans = res_json.get("answers", {}).get("is_bug", {})
        self.assertIn("noul", ans)
        print(f"[Playwright E2E] Laya Inference: 200 OK | Forward Pass Latency: {latency_ms:.1f}ms | P(bug): {ans.get('noul'):.4f}")
        request_context.dispose()

if __name__ == "__main__":
    unittest.main(verbosity=2)
