from playwright.sync_api import Locator


def parse_jobs(cards: Locator) -> list[dict]:
    return cards.evaluate_all(r"""
        cards => cards.flatMap(card => {
            const company =
                card.querySelector('a[href^="/company/"] h2')?.innerText.trim() || "-";

            const company_link =
                card.querySelector('a[href^="/company/"]')?.href || "-";

            const hiring =
                card.querySelector('div.text-pop-green')?.innerText.trim() || "-";

            const description =
                card.querySelector('span.text-xs.text-neutral-1000')?.innerText.trim() || "-";

            const employees =
                card.querySelector('span.text-xs.italic.text-neutral-500')?.innerText.trim() || "-";

            const currencyPattern =
                /[\$€£¥₹₩₺₽₴₦₱฿₫₪]|\b(zł|kr|CAD|CHF|AUD|NZD|SGD|HKD|MXN|BRL|ZAR|AED|SAR)\b/i;

            return [...card.querySelectorAll('a[href^="/jobs/"]')].map(job => {
                const spans = [
                    ...job.parentElement.parentElement.querySelectorAll('span.pl-1')
                ];

                return {
                    company,
                    company_link,
                    hiring,
                    description,
                    employees,

                    title: job.innerText.trim() || "-",
                    job_link: job.href || "-",

                    job_type:
                        job.nextElementSibling?.innerText.trim() || "-",

                    salary:
                        spans.find(el =>
                            currencyPattern.test(el.innerText.trim())
                        )?.innerText.trim() || "-",

                    experience:
                        spans.find(el =>
                            /years/i.test(el.innerText)
                        )?.innerText.trim() || "-",

                    location:
                        spans.find(el =>
                            !currencyPattern.test(el.innerText.trim()) &&
                            !/years/i.test(el.innerText.trim()) &&
                            !/experience/i.test(el.innerText.trim()) &&
                            !/equity/i.test(el.innerText.trim()) &&
                            !el.innerText.includes('%')
                        )?.innerText.trim() || "-",

                    posted:
                        card.querySelector(
                            'span.text-xs.lowercase.text-dark-a'
                        )?.innerText.trim() || "-"
                };
            });
        })
    """)