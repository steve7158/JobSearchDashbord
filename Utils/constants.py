import datetime


STYLES_STREAMLIT="""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
"""

FOOTER_HTML="""<div style='text-align: center; color: #666;'>
            💼 Job Portal Dashboard | Built with Streamlit & JobSpy
            </div>"""

COVER_LETTER_TEMPLATE="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cover Letter</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #fff;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            min-height: 11in;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 1rem;
        }}
        
        .applicant-name {{
            font-size: 2.2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
        }}
        
        .contact-info {{
            font-size: 1rem;
            color: #5d6d7e;
            line-height: 1.4;
        }}
        
        .contact-info a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .contact-info a:hover {{
            text-decoration: underline;
        }}
        
        .date-section {{
            text-align: right;
            margin: 2rem 0 1.5rem 0;
            font-size: 1rem;
            color: #5d6d7e;
        }}
        
        .employer-info {{
            margin-bottom: 2rem;
            line-height: 1.5;
        }}
        
        .employer-name {{
            font-weight: bold;
            font-size: 1.1rem;
            color: #2c3e50;
        }}
        
        .employer-title {{
            font-style: italic;
            color: #5d6d7e;
        }}
        
        .employer-company {{
            font-weight: 600;
            color: #34495e;
        }}
        
        .salutation {{
            margin: 2rem 0 1.5rem 0;
            font-size: 1.1rem;
            font-weight: 500;
        }}
        
        .content {{
            margin-bottom: 2rem;
        }}
        
        .paragraph {{
            margin-bottom: 1.5rem;
            text-align: justify;
            font-size: 1rem;
            line-height: 1.7;
        }}
        
        .paragraph:first-child {{
            margin-top: 0;
        }}
        
        .closing {{
            margin-top: 2.5rem;
        }}
        
        .closing-phrase {{
            margin-bottom: 3rem;
            font-size: 1rem;
        }}
        
        .signature-area {{
            margin-bottom: 1rem;
        }}
        
        .signature-line {{
            border-bottom: 1px solid #bdc3c7;
            width: 250px;
            height: 60px;
            margin-bottom: 0.5rem;
        }}
        
        .printed-name {{
            font-weight: bold;
            font-size: 1rem;
            color: #2c3e50;
        }}
        
        .highlight {{
            font-weight: 600;
            color: #2980b9;
        }}
        
        .position-title {{
            font-weight: bold;
            color: #e74c3c;
        }}
        
        /* Print to PDF button */
        .pdf-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #e74c3c;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .pdf-button:hover {{
            background-color: #c0392b;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0.75in;
                max-width: none;
            }}
            
            .header {{
                page-break-after: avoid;
            }}
            
            .paragraph {{
                page-break-inside: avoid;
            }}
            
            .pdf-button {{
                display: none;
            }}
        }}
    </style>
    <script>
        function printToPDF() {{
            // Trigger the browser's print dialog
            window.print();
        }}
        
        // Auto-focus on window load for better user experience
        window.onload = function() {{
            console.log('Cover letter loaded successfully');
        }}
    </script>
</head>
<body>
    <!-- Print to PDF Button -->
    <button class="pdf-button" onclick="printToPDF()">📄 Save as PDF</button>
    
    <div class="header">
        <div class="applicant-name">{data['applicant_name']}</div>
        <div class="contact-info">
            {data['phone']} • <a href="mailto:{data['email']}">{data['email']}</a><br>
            {data['address']}<br>
            <a href="{data['linkedin']}" target="_blank">LinkedIn</a> • <a href="{data['portfolio']}" target="_blank">Portfolio</a>
        </div>
    </div>
    
    <div class="date-section">
        {data['date']}
    </div>
    
    <div class="employer-info">
        <div class="employer-name">{data['hiring_manager_name']}</div>
        <div class="employer-title">{data['hiring_manager_title']}</div>
        <div class="employer-company">{data['company_name']}</div>
        <div>{data['company_address']}</div>
    </div>
    
    <div class="salutation">
        Dear {data['salutation']},
    </div>
    
    <div class="content">
        <div class="paragraph">
            I am writing to express my strong interest in the <span class="position-title">{data['position_title']}</span> position at <span class="highlight">{data['company_name']}</span>. {data['opening_paragraph']}
        </div>
        
        <div class="paragraph">
            {data['body_paragraph_1']}
        </div>
        
        <div class="paragraph">
            {data['body_paragraph_2']}
        </div>
        
        <div class="paragraph">
            {data['closing_paragraph']}
        </div>
    </div>
    
    <div class="closing">
        <div class="closing-phrase">
            Sincerely,
        </div>
        <div class="signature-area">
            <div class="signature-line"></div>
            <div class="printed-name">{data['applicant_name']}</div>
        </div>
    </div>
</body>
</html>
        """


COVER_LETTER_DATA_TEMPLATE={
        'applicant_name': 'John Doe',
        'phone': '(555) 123-4567',
        'email': 'john.doe@email.com',
        'address': '123 Main Street, City, State 12345',
        'linkedin': 'https://linkedin.com/in/johndoe',
        'portfolio': 'https://johndoe.dev',
        'date': datetime.now().strftime('%B %d, %Y'),
        'hiring_manager_name': 'Jane Smith',
        'hiring_manager_title': 'Hiring Manager',
        'company_name': 'TechCorp Industries',
        'company_address': '456 Business Ave, Corporate City, State 67890',
        'salutation': 'Ms. Smith',
        'position_title': 'Senior Software Developer',
        'opening_paragraph': 'With over 5 years of experience in full-stack development and a proven track record of delivering high-quality software solutions, I am excited about the opportunity to contribute to your innovative team.',
        'body_paragraph_1': 'In my previous role at ABC Technology, I successfully led the development of a microservices architecture that improved system performance by 40% and reduced deployment time by 60%. My expertise in Python, JavaScript, and cloud technologies, combined with my experience in agile development methodologies, makes me well-suited for this position.',
        'body_paragraph_2': 'I am particularly drawn to TechCorp Industries because of your commitment to cutting-edge technology and innovation. Your recent work on AI-driven solutions aligns perfectly with my passion for emerging technologies and my experience in machine learning implementations.',
        'closing_paragraph': 'I would welcome the opportunity to discuss how my technical skills and experience can contribute to your team\'s continued success. Thank you for considering my application. I look forward to hearing from you soon.'
    }

USER_DATA = {
    'applicant_name': 'John Doe',
    'phone': '(555) 123-4567',
    'email': 'john.doe@email.com',
    'address': '123 Main Street, City, State 12345',
    'linkedin': 'https://linkedin.com/in/johndoe',
    'portfolio': 'https://johndoe.dev',
    'date': datetime.now().strftime('%B %d, %Y'),
    'work_experiences': [
        {
            'company': 'ABC Technology',
            'position': 'Senior Software Developer',
            'duration': '2020-2023',
            'description': 'Led development of microservices architecture, improved system performance by 40%'
        },
        {
            'company': 'XYZ Solutions',
            'position': 'Full Stack Developer',
            'duration': '2018-2020',
            'description': 'Developed web applications using Python and JavaScript, managed database optimization'
        },
        {
            'company': 'StartupTech',
            'position': 'Junior Developer',
            'duration': '2016-2018',
            'description': 'Built responsive web interfaces, collaborated with cross-functional teams'
        }
    ],
    'skills': ['python', 'javascript', 'microservices', 'machine learning']
}