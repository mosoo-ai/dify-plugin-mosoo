import io
import json
import unittest
from pathlib import Path
from urllib.error import HTTPError

from tools.mosoo_client import MosooApiError, MosooClient


AGENT_ID = "01J00000000000000000000001"
THREAD_ID = "01J00000000000000000000002"
RUN_ID = "01J00000000000000000000003"


class FakeResponse:
    def __init__(self, body: dict, status: int = 200) -> None:
        self.body = json.dumps(body).encode()
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, _limit: int = -1) -> bytes:
        return self.body


class MosooClientTest(unittest.TestCase):
    def test_creates_thread_and_returns_canonical_final_output(self) -> None:
        requests = []
        responses = iter(
            [
                FakeResponse(
                    {
                        "run": {"id": RUN_ID, "status": "running"},
                        "thread": {"id": THREAD_ID, "userId": "dify-user"},
                    },
                    201,
                ),
                FakeResponse(
                    {
                        "run": {
                            "finalOutput": {"text": "canonical answer"},
                            "id": RUN_ID,
                            "status": "completed",
                        },
                        "thread": {"id": THREAD_ID, "userId": "dify-user"},
                    }
                ),
            ]
        )

        def opener(request, timeout):
            requests.append((request, timeout))
            return next(responses)

        result = MosooClient(
            "mst_testtoken", opener=opener, sleep=lambda _seconds: None
        ).run(
            agent_id=AGENT_ID,
            prompt="do the work",
            thread_id=None,
            timeout_seconds=10,
            user_id="dify-user",
        )

        self.assertEqual(result["text"], "canonical answer")
        self.assertEqual(result["thread_id"], THREAD_ID)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(json.loads(requests[0][0].data)["userId"], "dify-user")
        self.assertTrue(
            requests[0][0].get_header("Authorization").startswith("Bearer mst_")
        )
        self.assertIsNotNone(requests[0][0].get_header("Idempotency-key"))

    def test_rejects_cross_user_thread_before_sending_prompt(self) -> None:
        client = MosooClient(
            "mst_testtoken",
            opener=lambda _request, timeout: FakeResponse(
                {
                    "run": {"id": RUN_ID, "status": "running"},
                    "thread": {"userId": "other-user"},
                }
            ),
        )

        with self.assertRaisesRegex(ValueError, "current Dify user"):
            client.run(
                agent_id=AGENT_ID,
                prompt="continue",
                thread_id=THREAD_ID,
                timeout_seconds=10,
                user_id="dify-user",
            )

    def test_sanitizes_http_error_body(self) -> None:
        secret_message = "raw upstream details must not escape"

        def opener(request, timeout):
            raise HTTPError(
                request.full_url,
                401,
                "Unauthorized",
                {},
                io.BytesIO(
                    json.dumps(
                        {
                            "error": {
                                "code": "unauthenticated",
                                "message": secret_message,
                            }
                        }
                    ).encode()
                ),
            )

        with self.assertRaises(MosooApiError) as raised:
            MosooClient("mst_testtoken", opener=opener).list_threads(AGENT_ID)

        self.assertNotIn(secret_message, str(raised.exception))
        self.assertIn("Update the Dify plugin credentials", str(raised.exception))

    def test_readme_indexes_release_models_and_acp_agents(self) -> None:
        root = Path(__file__).parents[1]
        readme = (root / "README.md").read_text()
        model_ids = {
            "MiniMax-M2.7",
            "MiniMax-M3",
            "claude-fable-5",
            "claude-haiku-4-5",
            "claude-opus-4-5",
            "claude-opus-4-6",
            "claude-opus-4-7",
            "claude-sonnet-4-5",
            "claude-sonnet-4-6",
            "claude-sonnet-5",
            "deepseek-v4-flash",
            "deepseek-v4-pro",
            "gemini-3.5-flash",
            "glm-4.6",
            "glm-4.7",
            "glm-5.2",
            "gpt-5.2",
            "gpt-5.3",
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-5.5",
            "gpt-5.6-luna",
            "gpt-5.6-sol",
            "gpt-5.6-terra",
            "kimi-k2.6",
            "kimi-k2.7-code",
            "minimax-m2.7",
            "qwen3.6-plus",
            "qwen3.7-plus",
        }
        acp_ids = {
            "agoragentic-acp",
            "amp-acp",
            "auggie",
            "autohand",
            "claude-acp",
            "cline",
            "codebuddy-code",
            "codex-acp",
            "cortex-code",
            "corust-agent",
            "crow-cli",
            "cursor",
            "deepagents",
            "devin",
            "dimcode",
            "dirac",
            "factory-droid",
            "fast-agent",
            "gemini",
            "github-copilot",
            "github-copilot-cli",
            "glm-acp-agent",
            "goose",
            "grok-build",
            "harn",
            "junie",
            "kilo",
            "kimi",
            "minion-code",
            "mistral-vibe",
            "nova",
            "opencode",
            "pi-acp",
            "poolside",
            "qoder",
            "qwen-code",
            "sigit",
            "stakpak",
            "vtcode",
        }

        self.assertEqual(
            [item for item in model_ids | acp_ids if item not in readme], []
        )


if __name__ == "__main__":
    unittest.main()
