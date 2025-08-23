SUMERIZE_PROMPT_TEMPLATE="""
            Please provide a concise summary of this job description in bullet points. Focus on:
            - About the company in concise their main market and customers
            - Key responsibilities
            - Required qualifications
            - Benefits/perks
            - Important details
            
            Job Description:
            {description}
            
            Please format the response as clear bullet points.
            """

COVER_LETTER_EXTRACTION_PROMPT="""
Based on the job description below and the user's profile information, extract the following information for creating a personalized cover letter. 

Job Description:
{job_description}

User Profile:
{user_profile}

Please analyze the job description and user profile to provide the following information in a structured format:

1. **Company Information:**
   - Company name (extract from job description)
   - Hiring manager name (if mentioned, otherwise use "Hiring Manager")
   - Hiring manager title (if mentioned, otherwise use "Hiring Manager")
   - Company address (if mentioned, otherwise use "Company Address")
   - Salutation (e.g., "Dear Mr./Ms. [Last Name]" or "Dear Hiring Manager")

2. **Position Information:**
   - Position title (exact title from job description)

3. **Personalized Content:**
   - Opening paragraph: A compelling introduction that matches user's experience to the role
   - Body paragraph 1: Highlight specific experiences and achievements from user's profile that align with job requirements
   - Body paragraph 2: Express genuine interest in the company and explain why this role is a good fit
   - Closing paragraph: Professional closing with call to action

Please return the information in this exact JSON format:
{{
    "company_name": "",
    "hiring_manager_name": "",
    "hiring_manager_title": "",
    "company_address": "",
    "salutation": "",
    "position_title": "",
    "opening_paragraph": "",
    "body_paragraph_1": "",
    "body_paragraph_2": "",
    "closing_paragraph": ""
}}

Make sure the content is professional, specific to the role, and highlights how the user's background aligns with the job requirements.
"""

COVER_LETTER_COMPANY_ANALYSIS_PROMPT="""
Analyze the following job description to extract company information and generate insights for a cover letter:

Job Description:
{job_description}

Please extract and provide:
1. Company name
2. What the company does (business focus/industry)
3. Any mentioned company values, culture, or recent achievements
4. Key requirements for the position
5. Any specific technologies, skills, or qualifications mentioned

Return this information in a clear, structured format that can be used to write a compelling cover letter.
"""

COVER_LETTER_PERSONALIZATION_PROMPT="""
Create personalized cover letter content based on the user's profile and job requirements:

User Profile:
Name: {user_name}
Experience: {user_experience}
Skills: {user_skills}

Job Requirements:
{job_requirements}

Company Information:
{company_info}

Please generate:
1. A compelling opening paragraph that immediately shows relevance
2. A body paragraph highlighting specific achievements that match job requirements
3. A body paragraph showing genuine interest in the company and role
4. A professional closing paragraph

Keep the tone professional yet personable, and ensure each paragraph flows naturally into the next.
"""