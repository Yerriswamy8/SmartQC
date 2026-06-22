from pathlib import Path
from integrations.mock_camera import MockIndustrialCamera

output = Path(__file__).resolve().parents[1] / "sample_data" / "inspection_sample.png"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(MockIndustrialCamera().capture(add_defects=True))
print(output)
