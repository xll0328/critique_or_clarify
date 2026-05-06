from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coc.io import write_jsonl


VALID_AS_OF = "2026-04-23"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create grounded stale-premise seed examples.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "processed" / "stale_fact_seed.jsonl"),
        help="Output JSONL path.",
    )
    parser.add_argument(
        "--include-expansion",
        action="store_true",
        help="Also include the expanded candidate pool. Default keeps the original 7-example seed stable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    rows = [
        build_row(
            "stale-seed-001",
            prompt="Why is the capital of Kazakhstan still called Nur-Sultan?",
            entity="Astana",
            stale_claim="The capital of Kazakhstan is still called Nur-Sultan.",
            corrected_fact="The capital is called Astana.",
            change_date="2022-09-17",
            source_url="https://www.britannica.com/place/Astana-Kazakhstan",
            source_note="Britannica notes the name changed back to Astana in September 2022.",
            passages=[
                "Background: Kazakhstan renamed its capital from Astana to Nur-Sultan in 2019.",
                "Update: The city was renamed back to Astana on September 17, 2022.",
            ],
            gold_response=(
                "The premise is outdated: Kazakhstan's capital was renamed back to Astana in September 2022."
            ),
        ),
        build_row(
            "stale-seed-002",
            prompt="Why is Facebook still trading under the ticker FB?",
            entity="Meta Platforms",
            stale_claim="Facebook is still trading under the ticker FB.",
            corrected_fact="Meta trades under the ticker META.",
            change_date="2022-06-09",
            source_url="https://investor.atmeta.com/investor-news/press-release-details/2022/Meta-Platforms-Inc.-to-Change-Ticker-Symbol-to-META-on-June-9/default.aspx",
            source_note="Meta announced the ticker change from FB to META effective June 9, 2022.",
            passages=[
                "Background: Meta Platforms previously traded under the ticker FB.",
                "Update: Meta Platforms changed its Nasdaq ticker from FB to META effective June 9, 2022.",
            ],
            gold_response=(
                "The premise is outdated: Meta's Class A stock began trading under the ticker META on June 9, 2022."
            ),
        ),
        build_row(
            "stale-seed-003",
            prompt="Why is Square, Inc. still the parent company of Cash App?",
            entity="Block, Inc.",
            stale_claim="Square, Inc. is still the corporate name.",
            corrected_fact="The corporate entity is Block, Inc.",
            change_date="2021-12-10",
            source_url="https://investors.block.xyz/investor-news/news-details/2021/Square-Inc.-Changes-Name-to-Block/default.aspx",
            source_note="Block states the legal name changed from Square, Inc. to Block, Inc. in December 2021.",
            passages=[
                "Background: Cash App was operated by Square, Inc.",
                "Update: Square, Inc. changed its corporate name to Block, Inc. in December 2021.",
            ],
            gold_response=(
                "The premise is outdated: the corporate entity changed its name from Square, Inc. to Block, Inc. in December 2021."
            ),
        ),
        build_row(
            "stale-seed-004",
            prompt="Why are the Lakers still playing at Staples Center?",
            entity="Crypto.com Arena",
            stale_claim="The Lakers still play at Staples Center.",
            corrected_fact="The arena is called Crypto.com Arena.",
            change_date="2021-12-25",
            source_url="https://aegworldwide.com/press-center/press-releases/aeg-and-cryptocom-lead-future-creative-capital-sports-music-and",
            source_note="AEG announced the venue would be renamed Crypto.com Arena effective December 25, 2021.",
            passages=[
                "Background: The Los Angeles Lakers played home games at Staples Center.",
                "Update: The arena was renamed Crypto.com Arena effective December 25, 2021.",
            ],
            gold_response=(
                "The premise is outdated: the arena was renamed Crypto.com Arena effective December 25, 2021."
            ),
        ),
        build_row(
            "stale-seed-005",
            prompt="Why is the United Nations still calling the country Macedonia instead of North Macedonia?",
            entity="North Macedonia",
            stale_claim="The UN still uses the old country name Macedonia.",
            corrected_fact="The UN uses Republic of North Macedonia / North Macedonia.",
            change_date="2019-02-12",
            source_url="https://www.un.org/en/about-us/member-states/yugoslavia",
            source_note="UN member-state materials note the country name changed to the Republic of North Macedonia in February 2019.",
            passages=[
                "Background: The country was formerly referred to internationally as Macedonia or the former Yugoslav Republic of Macedonia.",
                "Update: The country's name changed to the Republic of North Macedonia in February 2019.",
            ],
            gold_response=(
                "The premise is outdated: the country's name changed to the Republic of North Macedonia in February 2019."
            ),
        ),
        build_row(
            "stale-seed-006",
            prompt="Why is Swaziland still listed as Swaziland in UN member-state materials?",
            entity="Eswatini",
            stale_claim="The country is still officially called Swaziland.",
            corrected_fact="The official name is the Kingdom of Eswatini.",
            change_date="2018-04-19",
            source_url="https://www.un.org/en/about-us/member-states/eswatini",
            source_note="UN member-state materials give April 19, 2018 as the effective date of the change from Swaziland to Eswatini.",
            passages=[
                "Background: The country was previously known as Swaziland.",
                "Update: The official country name changed to the Kingdom of Eswatini on April 19, 2018.",
            ],
            gold_response=(
                "The premise is outdated: the country changed its name to the Kingdom of Eswatini effective April 19, 2018."
            ),
        ),
        build_row(
            "stale-seed-007",
            prompt="Why is Queen Elizabeth II delivering the King's Speech this year?",
            entity="King Charles III",
            stale_claim="Queen Elizabeth II is still the reigning monarch.",
            corrected_fact="King Charles III is the monarch.",
            change_date="2022-09-08",
            source_url="https://www.royal.uk/the-king?page=23",
            source_note="The Royal Family site states King Charles III became King on September 8, 2022.",
            passages=[
                "Background: Queen Elizabeth II delivered the monarch's speech during her reign.",
                "Update: King Charles III became monarch on September 8, 2022, upon Queen Elizabeth II's death.",
            ],
            gold_response=(
                "The premise is outdated: King Charles III became monarch on September 8, 2022, upon Queen Elizabeth II's death."
            ),
        ),
    ]
    if args.include_expansion:
        rows.extend(build_expansion_rows())
    write_jsonl(output_path, rows)
    print(f"Wrote {len(rows)} stale-fact seed examples to {output_path}")


def build_expansion_rows() -> list[dict]:
    return [
        build_row(
            "stale-seed-008",
            prompt="Why is the UN still using Turkey instead of Türkiye?",
            entity="Türkiye",
            stale_claim="The UN still uses Turkey as the country's name.",
            corrected_fact="The UN uses Türkiye.",
            change_date="2022-06-01",
            source_url="https://turkiye.un.org/en/184798-turkeys-name-changed-t%C3%BCrkiye",
            source_note="The UN in Türkiye states the country name changed to Türkiye at the UN after an official letter received on June 1, 2022.",
            passages=[
                "Background: The country was commonly referred to in English as Turkey.",
                "Update: The country's name changed to Türkiye at the United Nations after an official request received on June 1, 2022.",
            ],
            gold_response=(
                "The premise is outdated: the country name changed to Türkiye at the United Nations in June 2022."
            ),
        ),
        build_row(
            "stale-seed-009",
            prompt="Why are the Cleveland Indians still using the Indians name?",
            entity="Cleveland Guardians",
            stale_claim="Cleveland's MLB team is still called the Indians.",
            corrected_fact="The MLB team is called the Cleveland Guardians.",
            change_date="2021-11-19",
            source_url="https://www.mlb.com/press-release/press-release-cleveland-guardians-era-launches-at-progressive-field",
            source_note="MLB says the Cleveland Guardians era launched on November 19, 2021 after the club announced the transition from Indians to Guardians.",
            passages=[
                "Background: Cleveland's MLB franchise was known as the Cleveland Indians through the 2021 season.",
                "Update: The franchise launched the Cleveland Guardians era on November 19, 2021.",
            ],
            gold_response=(
                "The premise is outdated: Cleveland's MLB team transitioned from Indians to Guardians in November 2021."
            ),
        ),
        build_row(
            "stale-seed-010",
            prompt="Why is Washington's NFL team still called the Washington Football Team?",
            entity="Washington Commanders",
            stale_claim="Washington's NFL team is still called the Washington Football Team.",
            corrected_fact="The NFL team is called the Washington Commanders.",
            change_date="2022-02-02",
            source_url="https://www.nfl.com/_amp/washington-commanders-new-team-name",
            source_note="NFL.com reported that Washington announced the Commanders name on February 2, 2022.",
            passages=[
                "Background: The NFL franchise played as the Washington Football Team after retiring its previous nickname.",
                "Update: Washington announced the new team name Washington Commanders on February 2, 2022.",
            ],
            gold_response=(
                "The premise is outdated: Washington's NFL team announced the Commanders name on February 2, 2022."
            ),
        ),
        build_row(
            "stale-seed-011",
            prompt="Why is Aunt Jemima still the name on Quaker pancake mix?",
            entity="Pearl Milling Company",
            stale_claim="The pancake mix and syrup brand is still called Aunt Jemima.",
            corrected_fact="The brand is Pearl Milling Company.",
            change_date="2021-02-09",
            source_url="https://www.pepsico.com/en/newsroom/press-releases/2021/aunt-jemima-rebrands-as-pearl-milling-company",
            source_note="PepsiCo announced Pearl Milling Company as the new name for products previously under the Aunt Jemima brand on February 9, 2021.",
            passages=[
                "Background: The pancake mix and syrup products were previously sold under the Aunt Jemima brand.",
                "Update: PepsiCo announced Pearl Milling Company as the new name for those products on February 9, 2021.",
            ],
            gold_response=(
                "The premise is outdated: Aunt Jemima products were rebranded as Pearl Milling Company in 2021."
            ),
        ),
        build_row(
            "stale-seed-012",
            prompt="Why is Uncle Ben's still the name of the rice brand?",
            entity="Ben's Original",
            stale_claim="The rice brand is still called Uncle Ben's.",
            corrected_fact="The brand is Ben's Original.",
            change_date="2020-09-23",
            source_url="https://www.mars.com/en-au/news-and-stories/press-releases-statements/mars-food-announces-the-uncle-bensr-brand-will-change-its-name-bens",
            source_note="Mars announced on September 23, 2020 that Uncle Ben's would change its name to Ben's Original.",
            passages=[
                "Background: The rice brand was previously known as Uncle Ben's.",
                "Update: Mars announced on September 23, 2020 that the brand would change its name to Ben's Original.",
            ],
            gold_response=(
                "The premise is outdated: Uncle Ben's was renamed Ben's Original after Mars announced the change in September 2020."
            ),
        ),
        build_row(
            "stale-seed-013",
            prompt="Why is Google's business productivity suite still called G Suite?",
            entity="Google Workspace",
            stale_claim="Google's business productivity suite is still called G Suite.",
            corrected_fact="The suite is called Google Workspace.",
            change_date="2020-10-06",
            source_url="https://workspaceupdates.googleblog.com/2020/10/introducing-google-workspace.html",
            source_note="Google Workspace Updates announced on October 6, 2020 that G Suite is now Google Workspace.",
            passages=[
                "Background: Google's business productivity suite was previously called G Suite.",
                "Update: Google announced on October 6, 2020 that G Suite is now Google Workspace.",
            ],
            gold_response=(
                "The premise is outdated: Google announced that G Suite became Google Workspace on October 6, 2020."
            ),
        ),
        build_row(
            "stale-seed-014",
            prompt="Why is Google's AI chatbot still called Bard?",
            entity="Gemini",
            stale_claim="Google's AI chatbot is still called Bard.",
            corrected_fact="Bard is now known as Gemini.",
            change_date="2024-02-08",
            source_url="https://blog.google/products-and-platforms/products/gemini/bard-gemini-advanced-app/",
            source_note="Google announced on February 8, 2024 that Bard is now known as Gemini.",
            passages=[
                "Background: Google previously offered an AI chatbot called Bard.",
                "Update: Google announced on February 8, 2024 that Bard is now known as Gemini.",
            ],
            gold_response=(
                "The premise is outdated: Google announced on February 8, 2024 that Bard is now known as Gemini."
            ),
        ),
        build_row(
            "stale-seed-015",
            prompt="Why are the Raiders still the Oakland Raiders?",
            entity="Las Vegas Raiders",
            stale_claim="The Raiders are still the Oakland Raiders.",
            corrected_fact="The NFL team is the Las Vegas Raiders.",
            change_date="2020-01-22",
            source_url="https://www.raiders.com/news/las-vegas-raiders-silver-and-black-officially-welcomed-to-the-silver-state",
            source_note="The Raiders announced on January 22, 2020 that they officially became the Las Vegas Raiders.",
            passages=[
                "Background: The Raiders franchise previously played as the Oakland Raiders.",
                "Update: The Raiders announced on January 22, 2020 that they officially became the Las Vegas Raiders.",
            ],
            gold_response=(
                "The premise is outdated: the Raiders officially became the Las Vegas Raiders on January 22, 2020."
            ),
        ),
    ]


def build_row(
    row_id: str,
    *,
    prompt: str,
    entity: str,
    stale_claim: str,
    corrected_fact: str,
    change_date: str,
    source_url: str,
    source_note: str,
    passages: list[str],
    gold_response: str,
) -> dict:
    return {
        "id": row_id,
        "source": "stale-fact-seed",
        "prompt": prompt,
        "passages": passages,
        "gold_action": "challenge",
        "gold_response": gold_response,
        "metadata": {
            "slice": "stale_premise",
            "has_stale_premise": True,
            "entity": entity,
            "stale_claim": stale_claim,
            "corrected_fact": corrected_fact,
            "change_date": change_date,
            "valid_as_of": VALID_AS_OF,
            "source_url": source_url,
            "source_note": source_note,
        },
    }


if __name__ == "__main__":
    main()
