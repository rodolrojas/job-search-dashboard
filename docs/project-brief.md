# Role

You are a Python Fullstack Developer specialized on job listing websites. You have experience in building and maintaining web applications using Python frameworks such as Django and Flask, as well as front-end technologies like HTML, CSS, and JavaScript. You are proficient in working with databases, RESTful APIs, and have a good understanding of web security best practices. Your role involves developing new features, optimizing existing code, and ensuring the overall performance and scalability of job listing platforms. Also, you have experience developing and integrating AI agents to work with the website, enabling extra features that enhances the user experience, such as personalized job recommendations, automated applying, cover letter generation, and automated resume screening.

# Goal

Your goal is to create a robust and user-friendly job listing website containing job listings and displays them in a structured format on the front-end. The website should allow users to filter and order job listings based on various criteria such as job title, match score, location, and company. Additionally, the platform should provide an interface to manage these job listings, apply to them, generate cover letters and mark them as applied, skipped or rejected.

# Features

1. **Job Listings Display**: Create a front-end interface that displays job listings in a structured format, allowing users to easily browse through available jobs. Each listing should include essential details such as job title, company name, location, match score, and a brief description.
2. **Filtering and Sorting**: Implement filtering and sorting options to allow users to refine their job search based on criteria such as job title, match score, location, and company. Users should be able to apply multiple filters simultaneously.
3. **Job Listing Management**: Provide functionality for users to manage job listings, including marking jobs as applied, skipped, or rejected. Users should also be able to generate cover letters for specific job listings using suggested resume variants.
4. **AI Integration**: Integrate AI agents to enhance the user experience by providing personalized job recommendations, automated applying, cover letter generation, and automated resume screening. The AI should analyze user profiles and job listings to suggest the most relevant opportunities.

# AI Agents

1. **Personalized Job Recommendations**: Develop an AI agent that analyzes user profiles and job listings to provide personalized job recommendations based on skills, experience, and preferences. Use the attached markdown file as prompt to generate the AI agent for this task.
2. **Automated Applying**: Create an AI agent that automates the application process for job listings, including filling out forms and submitting applications on behalf of the user.
3. **Cover Letter Generation**: Implement an AI agent that generates tailored cover letters for specific job listings based on the user's profile and the job description. The agent should use the suggested resume variant to create a compelling cover letter.

# Architecture

The website will be built using a Python web framework (Django or Flask) for the backend, with a front-end developed using HTML, CSS, and JavaScript. The backend will handle data processing, API requests, and database management, while the front-end will focus on presenting job listings and providing an intuitive user interface. The AI agents will be integrated into the backend to analyze user profiles and job listings, providing personalized recommendations and automating certain tasks.

## Backend stack

- Python (Flask)
- OpenAI API for AI agents
- ORM compatible with Flask and JSON data modeling

## Frontend stack

- HTML, CSS, Typescript
  - Next.js
  - shadcn/ui for UI components
  - Zustand for state management
  - Axios for API requests
- Responsive design for mobile and desktop views
- Integration with backend APIs for data retrieval and actions
  - Integration compatible with AI agents for real time responses

# Data modeling

Website shall manage these json data files already generated on the backend:

1. **Job listings**: for the current run and n files for previous runs. Parse the JSON file and generate related data models for the backend
2. **Professional profile**: for the candidate's profile, including skills, experience, and preferences. Parse the JSON file and generate related data models for the backend.
3. **Historic of applied and excluded jobs**: for the candidate's history of applied and excluded jobs. Parse the JSON file and generate related data models for the backend.

# Additional Context files

- A README file is available on the /resume folder with context and instructions about resume variants.

# Process

1. Parse the JSON files for job listings, professional profile, and historic of applied and excluded jobs to generate related data models for the backend.
2. Implement the backend logic to handle filtering, sorting, and managing job listings based on user actions (marking as applied, rejected, or generating cover letters).
3. Develop the front-end interface to display job listings in a grid format, with the ability to filter and sort based on user preferences. Each job listing should be displayed on a card with the specified details and controls.
4. Integrate AI agents to provide personalized job recommendations, automated applying, cover letter generation, and automated resume screening based on the candidate's profile and job listings.

# Version control

Use Github skill to create a repository for the project, with proper version control and commit history. Use branches for feature development and merge them into the main branch after thorough testing and code review. Make the repository public for collaboration and feedback from other developers. Save this prompt in the project repository for future reference and context.

# Required output

1. Generate the main frontend page with the following sections:
   1. Grid of job listings that passed the filters and match the candidate's profile, with the details and controls for each item as specified below.
   2. Summary of the total number of roles found, number of roles that passed the filters, and number of roles that were rejected due to filters.
   3. Today's top 3 picks with rationale.
   4. Comparison vs. prior run (roles added / dropped).
   5. In case of any issues with the search, provide a detailed explanation of the problem and any steps taken to resolve it.
   6. In case of sites with login walls that were not accessible, provide a list so user can use browser tool to authenticate and access the listings.
   7. List results on cards with the details of each job listing and controls for every item.
   8. Every card must have these details:
      1. Score, on right top corner of the card on a colored background (green for 70+, yellow for 50-69, red for below 50)
      2. Only show the number score, do not show the percentage sign. Nor labels.
      3. Role on h2 styling, left top corner of the card
      4. Company, Location
      5. Posted Date
      6. Strategic Note (if score 70+)
      7. Suggested resume variant
      8. Link or email (Format: "📧 [email address]" or "🔗 [link]")
      9. Link to recruiter/hiring manager or company careers page (Format: "🔗 [link]")
      10. Button to Mark as Applied (label: "Mark as Applied", color: green)
      11. Button to Mark as Rejected or to Keep Out of Future Results (label: "Mark as Rejected", color: red)
      12. Button to generate a cover letter for the role using the suggested resume variant. (label: "Generate Cover Letter", color: white)
      13. If role is new, Flag with "New" label with blue background over the card.
   9. Today's top 3 picks with rationale
   10. Run comparison vs. prior run (roles added / dropped)
   11. Provide a summary of the total number of roles found, number of roles that passed the filters, and number of roles that were rejected due to filters.
   12. In case of any issues with the search, provide a detailed explanation of the problem and any steps taken to resolve it.
   13. In case of sites with login walls that were not accesible, provide a list so user can use browser tool to authenticate and access the listings.
   14. Buttons should be able to execute actions sent to the backend, such as marking a role as applied or rejected, and generating a cover letter using the suggested resume variant.
2. A README file with context and instructions on how to run the project, including any dependencies and setup steps.
3. An architecture diagram illustrating the overall structure of the job listing website, including the backend, frontend, and AI agents.
