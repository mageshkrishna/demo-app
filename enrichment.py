import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnrichmentService:
    def __init__(self, secrets):
        self.jina_api_key = secrets['JINA_API_KEY']
        self.hunter_api_key = secrets['HUNTER_API_KEY']
        self.gemini_api_key = secrets['GEMINI_API_KEY']
    
    def enrich_company_data(self, company_url, company_name, project_type):
        """Main enrichment orchestration"""
        logger.info(f"Starting enrichment for {company_name} (Project: {project_type})")
        
        jina_content = self._scrape_with_jina(company_url)
        social_media = self._extract_social_media(company_url)
        contact_data = self._find_contacts_with_hunter(company_url)
        
        enrichment_markdown = self._generate_enrichment_with_gemini(
            company_url,
            company_name,
            jina_content,
            social_media,
            contact_data,
            project_type
        )
        
        return enrichment_markdown
    
    def _scrape_with_jina(self, url):
        """Scrape website content using Jina AI"""
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                'Authorization': f'Bearer {self.jina_api_key}',
                'X-Return-Format': 'text'
            }
            
            response = requests.get(jina_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                logger.info(f"Jina scraped {len(content)} characters")
                return content[:10000]
            else:
                logger.warning(f"Jina scraping failed: {response.status_code}")
                return ''
        except Exception as e:
            logger.error(f"Jina error: {str(e)}")
            return ''
    
    def _extract_social_media(self, url):
        """Extract social media profiles from HTML"""
        try:
            response = requests.get(url, timeout=15)
            html = response.text
            
            patterns = {
                'LinkedIn': r'linkedin\.com/(?:company|in)/[\w-]+',
                'X': r'(?:twitter\.com|x\.com)/[\w]+',
                'Facebook': r'facebook\.com/[\w.-]+',
                'Instagram': r'instagram\.com/[\w.]+',
                'YouTube': r'youtube\.com/(?:c|channel|user|@)/[\w-]+',
                'TikTok': r'tiktok\.com/@[\w.]+'
            }
            
            import re
            found = {}
            
            for platform, pattern in patterns.items():
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    clean_url = matches[0]
                    if not clean_url.startswith('http'):
                        clean_url = 'https://' + clean_url
                    clean_url = clean_url.split('?')[0].split('#')[0].rstrip('/')
                    found[platform] = clean_url
            
            logger.info(f"Found {len(found)} social media profiles")
            return found
        except Exception as e:
            logger.error(f"Social media extraction error: {str(e)}")
            return {}
    
    def _find_contacts_with_hunter(self, url):
        """Find contacts using Hunter.io API"""
        try:
            domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            api_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hunter_api_key}"
            
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data') and data['data'].get('emails'):
                    personnel = []
                    generic_emails = []
                    
                    for email in data['data']['emails']:
                        if not email.get('value'):
                            continue
                        
                        if email.get('type') == 'personal' and (email.get('first_name') or email.get('last_name') or email.get('position')):
                            personnel.append({
                                'name': ' '.join(filter(None, [email.get('first_name'), email.get('last_name')])) or 'N/A',
                                'position': email.get('position', 'N/A'),
                                'email': email['value'],
                                'linkedin': email.get('linkedin', ''),
                                'twitter': email.get('twitter', '')
                            })
                        elif email.get('type') == 'generic':
                            generic_emails.append(email['value'])
                    
                    logger.info(f"Hunter found {len(personnel)} personnel, {len(generic_emails)} generic emails")
                    return {'personnel': personnel, 'genericEmails': generic_emails[:3]}
            else:
                logger.warning(f"Hunter API error: {response.status_code}")
            
            return {'personnel': [], 'genericEmails': []}
        except Exception as e:
            logger.error(f"Hunter error: {str(e)}")
            return {'personnel': [], 'genericEmails': []}
    
    def _generate_enrichment_with_gemini(self, company_url, company_name, jina_content, social_media, contact_data, project_type):
        """Generate enrichment report using Google Gemini"""
        try:
            contacts_table = self._format_contacts_table(contact_data['personnel'], contact_data['genericEmails'])
            social_media_section = self._format_social_media(social_media)
            
            prompt = self._build_prompt(
                company_url,
                company_name,
                jina_content,
                contacts_table,
                social_media_section,
                project_type
            )

            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"

            payload = {
                'contents': [{
                    'parts': [{'text': prompt}]
                }],
                'generationConfig': {
                    'temperature': 0.3,
                    'maxOutputTokens': 8192
                }
            }
            
            logger.info(f"Calling Gemini API for {company_name}")
            response = requests.post(api_url, json=payload, timeout=60)
            
            logger.info(f"Gemini response code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'candidates' in data and len(data['candidates']) > 0 and 'content' in data['candidates'][0]:
                    analysis = data['candidates'][0]['content']['parts'][0]['text']
                    logger.info(f"Gemini generated {len(analysis)} characters")
                    return analysis
                else:
                    error_msg = f"Unexpected API response structure: {str(data)[:500]}"
                    logger.error(error_msg)
                    return f"# Enrichment Error\n\n{error_msg}"
            else:
                error_text = response.text[:500]
                logger.error(f"Gemini API error {response.status_code}: {error_text}")
                return f"# Enrichment Error\n\nGemini API returned error {response.status_code} for {company_name}\n\nDetails: {error_text}"
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}", exc_info=True)
            return f"# Enrichment Error\n\nException: {str(e)}"
    
    def _build_prompt(self, company_url, company_name, jina_content, contacts_table, social_media_section, project_type):
        """Build prompt for Gemini"""
        context_headers = {
            'dataflow': """## 🎯 Dataflow Platform Opportunity

Dataflow is your all-in-one platform for building, deploying, and managing complex data workflows with speed and efficiency.

**How Dataflow Empowers Organizations:**
- **Simplify data engineering workflows** - Build, test, and deploy scalable data pipelines seamlessly
- **Accelerate analytics and AI projects** - Run data processing, ML, and analytics on a unified platform
- **Ensure reliability and scalability** - Cloud-native infrastructure that scales with your workloads
""",
            'dbo': """## 💼 Digital Back Office Services

Digital Back Office delivers business efficiency through AI transformation and data excellence.

**Our Expertise:**
- **AI Transformation** - Custom AI solutions for business automation
- **Data Strategy** - Strategic consulting for data-driven decision making
- **Data Engineering** - Scalable data infrastructure and pipelines
- **Data Science** - Advanced analytics and machine learning solutions
""",
            'kiran': """## 🌱 Kiran Foundation Partnership Opportunity

Kiran Foundation empowers exceptionally talented students from under-resourced families to realize their dreams.

**Our Mission:**
- **Empowering talented students** - Helping them achieve their educational and career aspirations
- **Creating space for women** - Programs for women to learn, grow, and lead
- **Building confidence** - Through free accessible resources and education

**Partnership Opportunities:**
- CSR program collaboration
- Talent development initiatives
- Educational sponsorships
- Women empowerment programs
"""
        }
        
        context_header = context_headers.get(project_type, '')
        
        prompt = f"""Analyze company and create detailed enrichment report.

WEBSITE: {company_url}
COMPANY: {company_name}
PROJECT: {project_type}

CONTENT:
{jina_content[:2500]}

CONTACTS:
{contacts_table}

SOCIAL MEDIA:
{social_media_section}

Generate GitHub Flavored Markdown report:

# 📊 {company_name} - Enrichment Report

**Website:** {company_url}
**Generated:** {datetime.now().strftime('%Y-%m-%d')}

---

{context_header}

---

## 🏢 Company Introduction

2-3 sentences: what they do, products/services, target market

## ⚡ Key {'Partnership Opportunities' if project_type == 'kiran' else 'Pain Points'}

1. **[Name]**: description
2. **[Name]**: description
3. **[Name]**: description
4. **[Name]**: description

## 💡 How We Can Help

### {'Platform Capabilities' if project_type == 'dataflow' else 'AI Transformation' if project_type == 'dbo' else 'Partnership Programs'}
- Solution 1
- Solution 2

### {'Benefits' if project_type == 'dataflow' else 'Data Strategy' if project_type == 'dbo' else 'Impact Areas'}
- Benefit 1
- Benefit 2

{'### Data Engineering\n- Engineering 1\n- Engineering 2\n\n### Data Science\n- Science 1\n- Science 2' if project_type == 'dbo' else ''}

## 📞 Contact Information

{contacts_table}

## 🌐 Social Media Profiles

{social_media_section}

## 📧 Outreach Strategy

### Email Templates

Create 3 email variations based on contact availability:
- If personnel contacts exist: personalized emails addressing specific roles
- If only generic emails: professional inquiry emails
- Each email should be concise, human-tone, engaging

### LinkedIn Messages

Create 2-3 LinkedIn DM variations:
- Connection requests
- Follow-up messages
- Keep under 250 characters each

---

Write complete, professional, human-like content. No placeholders. Reference actual company information."""
        
        return prompt
    
    def _format_contacts_table(self, personnel, generic_emails):
        """Format contacts as markdown table"""
        if not personnel and not generic_emails:
            return 'No contact information found'
        
        table = ''
        
        if personnel:
            table += '\n**Key Personnel:**\n\n'
            table += '| Name | Position | Email | LinkedIn | Twitter |\n'
            table += '|------|----------|-------|----------|----------|\n'
            
            for person in personnel:
                linkedin = f"[Profile]({person['linkedin']})" if person['linkedin'] else 'N/A'
                twitter = f"[Profile]({person['twitter']})" if person['twitter'] else 'N/A'
                table += f"| {person['name']} | {person['position']} | {person['email']} | {linkedin} | {twitter} |\n"
        
        if generic_emails:
            table += '\n**General Contact Emails:**\n'
            for email in generic_emails:
                table += f"- {email}\n"
        
        return table
    
    def _format_social_media(self, social_media):
        """Format social media profiles"""
        if not social_media:
            return 'No social media profiles found'
        
        output = '\n'
        for platform, url in social_media.items():
            output += f"- **{platform}**: {url}\n"
        return output
