import json
import anthropic
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings
from scholarships.models import Scholarship


COUNTRIES = [
    'indonesia', 'malaysia', 'thailand',
    'taiwan', 'japan', 'singapore', 'china'
]

PROMPT = """
Find exactly 3 real fully funded scholarships for international students (especially from Mali/Africa) to study in {country}.

Return ONLY a valid JSON array of exactly 3 objects. No markdown, no explanation, no code fences.
Each object must have exactly these fields:
- title: string
- country: string (must be: {country})
- university: string
- level: string (one of: bachelor, master, phd, short)
- description: string (2 sentences max)
- benefits: string (benefits separated by newline)
- requirements: string (requirements separated by newline)
- deadline: string (YYYY-MM-DD format, must be a future date after {today})
- link: string (official URL)
- is_featured: boolean

Today is {today}. Only include fully funded scholarships. Deadlines must be in the future.
""".strip()


class Command(BaseCommand):
    help = 'Sync fully funded scholarships using Claude AI'

    def handle(self, *args, **kwargs):
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        created = 0
        updated = 0

        for country in COUNTRIES:
            self.stdout.write(f'\n🌏 Researching {country.title()}...')

            try:
                message = client.messages.create(
                    model='claude-sonnet-4-6',
                    max_tokens=2048,
                    messages=[
                        {
                            'role': 'user',
                            'content': PROMPT.format(
                                country=country,
                                today=date.today().isoformat()
                            )
                        }
                    ]
                )

                raw = message.content[0].text.strip()

                # Strip markdown fences if present
                if '```' in raw:
                    raw = raw.split('```')[1]
                    if raw.startswith('json'):
                        raw = raw[4:]
                raw = raw.strip()

                scholarships = json.loads(raw)

            except json.JSONDecodeError as e:
                self.stderr.write(f'❌ JSON error for {country}: {e}')
                continue
            except Exception as e:
                self.stderr.write(f'❌ API error for {country}: {e}')
                continue

            for data in scholarships:
                try:
                    deadline_str = data.get('deadline', '')
                    try:
                        deadline = date.fromisoformat(deadline_str)
                    except ValueError:
                        self.stdout.write(f'  ⚠️  Bad deadline for {data.get("title")}: {deadline_str}')
                        continue

                    if deadline < date.today():
                        self.stdout.write(f'  ⏭️  Past deadline, skipping: {data.get("title")} ({deadline})')
                        continue

                    level_raw = data.get('level', '').lower().strip()
                    valid_levels = [l[0] for l in Scholarship.LEVEL_CHOICES]
                    if level_raw not in valid_levels:
                        level_raw = 'master'

                    obj, was_created = Scholarship.objects.update_or_create(
                        title=data['title'],
                        defaults={
                            'country':      country,
                            'university':   data.get('university', ''),
                            'level':        level_raw,
                            'description':  data.get('description', ''),
                            'benefits':     data.get('benefits', ''),
                            'requirements': data.get('requirements', ''),
                            'deadline':     deadline,
                            'link':         data.get('link', ''),
                            'is_featured':  data.get('is_featured', False),
                            'is_active':    True,
                        }
                    )

                    if was_created:
                        created += 1
                        self.stdout.write(f'  ✅ Created: {obj.title} — {deadline}')
                    else:
                        updated += 1
                        self.stdout.write(f'  🔄 Updated: {obj.title} — {deadline}')

                except Exception as e:
                    self.stdout.write(f'  ❌ Error: {data.get("title", "unknown")}: {e}')

        self.stdout.write(f'\n🎉 Done — {created} created, {updated} updated.')
