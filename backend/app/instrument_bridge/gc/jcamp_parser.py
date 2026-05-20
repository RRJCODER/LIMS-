"""JCAMP-DX 5.01/6.0 chromatogram parser for GC fatty acid results."""
import re
from dataclasses import dataclass, field


@dataclass
class GCPeak:
    retention_time_min: float
    area: float
    area_percent: float
    name: str | None = None
    height: float | None = None


class JCAMPParser:
    """
    Parses JCAMP-DX files produced by Agilent ChemStation, Shimadzu LabSolutions, etc.
    Extracts peaks from ##PEAK TABLE= blocks.
    """

    def parse(self, content: str) -> list[GCPeak]:
        peaks: list[GCPeak] = []
        in_peak_table = False

        for line in content.splitlines():
            line = line.strip()
            if line.upper().startswith("##PEAK TABLE="):
                in_peak_table = True
                continue
            if in_peak_table:
                if line.startswith("##"):
                    break
                if not line or line.startswith("$") or line.startswith(";"):
                    continue
                # Split on delimiters but preserve compound name (may contain spaces)
                # Format: RT, Area, Area%, Name (rest of line after 3rd field)
                parts = re.split(r"[,;]\s*", line, maxsplit=3)
                if len(parts) < 2:
                    parts = re.split(r"\s+", line, maxsplit=3)
                try:
                    rt = float(parts[0].strip())
                    area = float(parts[1].strip())
                    area_pct = float(parts[2].strip()) if len(parts) > 2 else 0.0
                    name = parts[3].strip() if len(parts) > 3 else None
                    peaks.append(GCPeak(retention_time_min=rt, area=area, area_percent=area_pct, name=name))
                except (ValueError, IndexError):
                    continue

        return peaks


class GCCSVParser:
    """Flexible CSV chromatogram parser. Detects delimiter and column names."""

    COLUMN_ALIASES = {
        "retention_time_min": ["retention time", "rt", "time", "tiempo de retención"],
        "area": ["area", "área", "peak area"],
        "area_percent": ["area%", "area %", "% area", "area percent"],
        "name": ["name", "compound", "peak name", "nombre"],
        "height": ["height", "altura"],
    }

    def parse(self, content: str) -> list[GCPeak]:
        import csv
        import io

        try:
            dialect = csv.Sniffer().sniff(content[:2048])
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(io.StringIO(content), dialect=dialect)
        if not reader.fieldnames:
            return []

        col_map = self._map_columns(reader.fieldnames)
        peaks: list[GCPeak] = []

        for row in reader:
            try:
                rt_col = col_map.get("retention_time_min")
                area_col = col_map.get("area")
                if not rt_col or not area_col:
                    continue
                rt = float(row[rt_col])
                area = float(row[area_col])
                area_pct_col = col_map.get("area_percent")
                area_pct = float(row[area_pct_col]) if area_pct_col and row.get(area_pct_col) else 0.0
                name_col = col_map.get("name")
                name = row[name_col].strip() if name_col and row.get(name_col) else None
                height_col = col_map.get("height")
                height = float(row[height_col]) if height_col and row.get(height_col) else None
                peaks.append(GCPeak(retention_time_min=rt, area=area, area_percent=area_pct, name=name, height=height))
            except (ValueError, KeyError):
                continue

        return peaks

    def _map_columns(self, fieldnames: list[str]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        lower_fields = {f.lower().strip(): f for f in fieldnames}
        for canonical, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias.lower() in lower_fields:
                    mapping[canonical] = lower_fields[alias.lower()]
                    break
        return mapping
