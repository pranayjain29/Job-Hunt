from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from typing import List, Optional
from datetime import datetime
import uuid
import re

from ..config import TARGET_ROLES, LOCATIONS, EXPERIENCE_RANGE
from ..models import JobPosting


class NaukriScraper:
    BASE_URL = "https://www.naukri.com"

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        self.page = await self.browser.new_page()
        
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def _build_search_url(self, role: str, location: str) -> str:
        role_param = role.lower().replace(" ", "-")
        location_param = location.lower().replace(" ", "-")
        return f"{self.BASE_URL}/{role_param}-jobs-in-{location_param}"

    def _parse_experience(self, exp_text: str) -> int:
        try:
            nums = re.findall(r'\d+', exp_text)
            if nums:
                return int(nums[0])
            return 0
        except (ValueError, IndexError):
            return 0

    def _generate_job_id(self, title: str, company: str) -> str:
        return str(uuid.uuid4())[:8]

    async def scrape_role(self, role: str, location: str) -> List[JobPosting]:
        jobs = []
        url = self._build_search_url(role, location)

        print(f"Loading: {url}")

        try:
            await self.page.goto(url, timeout=30000)
            await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            await self.page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            print(f"Timeout loading {role} in {location}")
            return jobs

        html = await self.page.content()
        print(f"Page length: {len(html)} chars")
        
        if len(html) < 1000:
            print(f"Blocked - page too short")
            return jobs

        job_cards = await self.page.query_selector_all(".srp-jobtuple-wrapper")

        if not job_cards:
            print(f"No jobs found for {role} in {location}")
            return jobs

        print(f"Found {len(job_cards)} job cards")

        for card in job_cards:
            try:
                title_elem = await card.query_selector(".title")
                company_elem = await card.query_selector(".comp-name")
                location_elem = await card.query_selector(".loc-wrap")
                experience_elem = await card.query_selector(".exp-wrap")
                date_elem = await card.query_selector(".job-post-day")

                if not title_elem:
                    continue

                title = (await title_elem.inner_text()).strip()
                company = (await company_elem.inner_text()).strip() if company_elem else "Unknown"
                location_text = (await location_elem.inner_text()).strip() if location_elem else location
                exp_text = (await experience_elem.inner_text()).strip() if experience_elem else "0-0"
                date_text = (await date_elem.inner_text()).strip() if date_elem else ""
                href = (await title_elem.get_attribute("href")) if title_elem else ""
                job_url = href if href.startswith("http") else self.BASE_URL + href

                experience = self._parse_experience(exp_text)

                if experience < EXPERIENCE_RANGE[0] or experience > EXPERIENCE_RANGE[1]:
                    continue

                tags_elem = await card.query_selector(".tags-gt")
                skills_list = []
                if tags_elem:
                    tag_items = await tags_elem.query_selector_all("li, span")
                    for tag in tag_items:
                        skill = (await tag.inner_text()).strip()
                        if skill:
                            skills_list.append(skill)

                jobs.append(JobPosting(
                    job_id=self._generate_job_id(title, company),
                    title=title,
                    company=company,
                    location=location_text,
                    experience_required=experience,
                    description=exp_text,
                    skills=skills_list[:5],
                    source="Naukri",
                    url=job_url,
                    posted_date=datetime.now(),
                ))

            except Exception as e:
                continue

        return jobs

    async def scrape_all(self) -> List[JobPosting]:
        all_jobs = []

        for role in TARGET_ROLES:
            for location in LOCATIONS:
                jobs = await self.scrape_role(role, location)
                all_jobs.extend(jobs)
                print(f"Collected {len(jobs)} jobs for {role} in {location}")

        return all_jobs


async def scrape() -> List[JobPosting]:
    async with NaukriScraper() as scraper:
        return await scraper.scrape_all()


class NaukriScraperRunner:
    @staticmethod
    async def run_async() -> List[JobPosting]:
        return await scrape()
    
    @staticmethod
    def run() -> List[JobPosting]:
        return asyncio.run(scrape())


if __name__ == "__main__":
    jobs = NaukriScraperRunner.run()
    print(f"\nTotal jobs scraped: {len(jobs)}")
    for job in jobs[:5]:
        print(f"- {job.title} at {job.company} ({job.location}, {job.experience_required} yrs)")