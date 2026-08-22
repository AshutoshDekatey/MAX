from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP = REPO_ROOT / "frontend" / "streamlit" / "app.py"


def test_v0_streamlit_app_and_system_flow_dialog_render_without_errors():
    app = AppTest.from_file(str(APP), default_timeout=20).run()

    assert not app.exception
    assert [title.value for title in app.title] == ["Project MAX — V0: The Dirty Bank"]
    assert [button.label for button in app.button] == [
        "View System Flow",
        "Generate customers",
        "Generate transactions",
        "Generate fraud",
        "Create bad records",
    ]

    app.button[0].click().run()
    assert not app.exception
    assert len(app.get("dialog")) == 1
