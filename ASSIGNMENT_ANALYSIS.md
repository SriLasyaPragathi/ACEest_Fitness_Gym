# DevOps Assignment 1 - Complete Requirements Analysis

**Course:** Introduction to DEVOPS (Merged - CSIZG514/SEZG514/SEUSZG514)(S2-25)  
**Assignment:** Assignment 1  
**Document Extracted From:** Introduction to DevOps Assignment - 1 2026.docx

---

## ASSIGNMENT OVERVIEW

**Title:** Implementing Automated CI/CD Pipelines for ACEest Fitness & Gym

### Objective
This assignment is designed to provide students with comprehensive, hands-on experience in modern DevOps methodologies. By executing this project, students will attain professional proficiency in:
- **Version Control** (Git/GitHub)
- **Containerization** (Docker)
- **Continuous Integration and Continuous Delivery (CI/CD)** pipelines using GitHub Actions and Jenkins

---

## PROBLEM STATEMENT

You have been appointed as a **Junior DevOps Engineer** for **ACEest Fitness & Gym**, a rapidly scaling startup.

### Your Mission
Architect and implement a robust, automated deployment workflow that guarantees:
- Code integrity
- Environmental consistency
- Rapid delivery

### Key Requirement
Your solution must transition the application through a rigorous lifecycle—from local development to an automated **Jenkins BUILD** environment.

---

## CORE ASSIGNMENT PHASES

### Phase 1: Application Development & Modularization
**Objective:** Develop a foundational Flask web application tailored for fitness and gym management.

**Key Details:**
- Use **Flask** framework as the base
- You will be provided with a baseline Python script to initialize the core logic and service endpoints
- Develop core Flask application with service endpoints for fitness/gym operations

**Deliverables:**
- `app.py` - Main Flask application file
- `requirements.txt` - Python dependencies file

---

### Phase 2: Version Control System (VCS) Strategy
**Objective:** Initialize version control and establish GitHub integration

**Requirements:**
- Initialize a local **Git** repository
- Synchronize with a remote **GitHub** counterpart
- Follow industry standards for versioning:
  - Descriptive commit messages (meaningful and logically structured)
  - Branch management for tracking:
    - Features
    - Bug fixes
    - Infrastructure updates

**Evaluation Criteria:**
- Git commits must be meaningful and logically structured
- Demonstrate professional VCS maturity

---

### Phase 3: Unit Testing & Validation Framework
**Objective:** Develop comprehensive unit tests for the Flask application

**Requirements:**
- Integrate the **Pytest** framework
- Develop a comprehensive suite of unit tests
- Tests must validate the internal logic of the Flask application
- Ensure all components perform according to specification before reaching the build stage

**Deliverables:**
- All Pytest test script files (comprehensive test coverage)

**Evaluation Criteria:**
- Pytest cases must effectively cover core functionalities
- Testing coverage must be adequate for all Flask components

---

### Phase 4: Containerization with Docker
**Objective:** Encapsulate the application in a portable Docker container

**Requirements:**
- Create a **Dockerfile** that includes:
  - Flask application
  - Environment and dependencies
  - All necessary configurations
- Ensure "write once, run anywhere" consistency
- Eliminate "it works on my machine" syndrome during transition from testing to production

**Key Principle:**
Docker ensures environment consistency across development, testing, and production

**Evaluation Criteria:**
- Dockerfile must be optimized for:
  - Size efficiency
  - Security best practices

**Deliverables:**
- Functional Dockerfile

---

### Phase 5: The Jenkins BUILD & Quality Gate
**Objective:** Integrate Jenkins server for automated builds

**Requirements:**
- Configure a Jenkins server to handle the primary **BUILD** phase
- Configure a Jenkins project that:
  - Pulls the latest code from GitHub
  - Performs a clean build of the environment
  - Serves as a secondary validation layer

**Purpose:**
Ensure code compiles and integrates correctly in a controlled build environment

**Evaluation Criteria:**
- Jenkins BUILD must trigger and complete without errors
- Build environment must be clean and properly configured

---

### Phase 6: Automated CI/CD Pipeline via GitHub Actions
**Objective:** Design a fully automated pipeline using GitHub Actions

**Requirements:**

#### Configuration File
- Filename: `.github/workflows/main.yml`
- Location: In the GitHub repository

#### Trigger Events
The pipeline must be triggered by:
- Every push to the repository
- Every pull_request

#### Pipeline Stages (Critical Execution Steps)

##### Stage 1: Build & Lint
- **Purpose:** Compile the application and check for syntax errors
- **Action:** Verify code compiles correctly
- **Validation:** Check for syntax/linting errors

##### Stage 2: Docker Image Assembly
- **Purpose:** Build the Docker container
- **Action:** Successfully build the Docker image
- **Validation:** Ensure image builds without errors

##### Stage 3: Automated Testing
- **Purpose:** Execute tests in the containerized environment
- **Action:** Run the full Pytest suite inside the Docker container
- **Validation:** Confirm application stability through test results

**Evaluation Criteria:**
- GitHub Actions workflow must successfully pass Build and Test stages on every push
- Pipeline reliability and consistency

---

## REQUIRED DELIVERABLES

Students must submit a link to a **publicly accessible GitHub Repository** containing:

### 1. Source Code
- **File:** `app.py`
  - Main Flask application with all service endpoints
  - Implementation of fitness/gym management functionality
- **File:** `requirements.txt`
  - All Python dependencies required for the Flask application

### 2. Test Suite
- **Test Files:** All Pytest script files
  - Comprehensive unit test coverage
  - Tests for all core functionality
  - Tests validating internal logic

### 3. Infrastructure as Code
- **Dockerfile:** Functional, optimized Dockerfile
  - Encapsulates Flask application
  - Includes all dependencies
  - Optimized for size and security
- **GitHub Actions Configuration:** `.github/workflows/main.yml`
  - Defines complete CI/CD pipeline
  - Implements all three stages (Build & Lint, Docker Assembly, Testing)
  - Triggers on push and pull_request events

### 4. Documentation
- **File:** `README.md` (Professional Quality)
  - **Section 1:** Local setup and execution instructions
    - How to set up the development environment
    - How to run the Flask application locally
  - **Section 2:** Steps to run tests manually
    - How to execute Pytest suite
    - Expected test output
  - **Section 3:** High-level overview of Jenkins and GitHub Actions integration logic
    - Architecture explanation
    - Pipeline workflow description
    - Integration between tools

---

## EVALUATION CRITERIA

Submissions will be assessed on these professional benchmarks:

### 1. Application Integrity (Flask Application)
**Criterion:** Does the Flask application function as specified?
- Application must work correctly
- All endpoints must function properly
- Fitness/gym management features must operate as designed

### 2. VCS Maturity (Version Control)
**Criterion:** Are Git commits meaningful and logically structured?
- Commits should be focused and atomic
- Commit messages should be descriptive
- Branch management should follow industry standards

### 3. Testing Coverage (Pytest)
**Criterion:** Do the Pytest cases effectively cover core functionalities?
- Tests must cover all major features
- Tests must validate core logic
- Adequate coverage for production readiness

### 4. Docker Efficiency (Containerization)
**Criterion:** Is the Dockerfile optimized for size and security?
- Image size should be reasonable
- Should follow Docker best practices
- Security considerations (no unnecessary packages)
- Use appropriate base images

### 5. Pipeline Reliability (Jenkins & GitHub Actions)
**Criterion:** Jenkins BUILD Reliability
- Jenkins BUILD must trigger without errors
- Clean build environment
- Successful integration with GitHub

**Criterion:** GitHub Actions Workflow
- Must successfully pass Build and Test stages on every push
- Consistent and reliable execution
- All three stages must function correctly

### 6. Documentation Clarity (README)
**Criterion:** Is the README.md professional and easy to follow for other engineers?
- Clear setup instructions
- Complete testing documentation
- Professional tone and formatting
- Easy for external developers to understand and replicate

---

## TOOLS & TECHNOLOGIES REQUIRED

### Core Technologies
| Technology | Purpose | Version Details |
|---|---|---|
| **Flask** | Web Framework | Latest stable (Python-based) |
| **Python** | Programming Language | Python 3.x |
| **Pytest** | Testing Framework | Latest compatible with Flask |
| **Docker** | Containerization | Latest stable Docker Engine |
| **Git** | Version Control | Latest stable |
| **GitHub** | Remote Repository | Public repository required |
| **GitHub Actions** | CI/CD Automation | Built-in GitHub feature |
| **Jenkins** | Build Environment | Latest stable Jenkins |

### Naming & File Structure Conventions

#### Required File Names
```
app.py                          # Flask application
requirements.txt               # Python dependencies
Dockerfile                      # Container configuration
.github/workflows/main.yml      # GitHub Actions workflow
README.md                       # Documentation
test_*.py                       # Pytest test files (recommended naming)
```

#### Repository Structure (Expected)
```
repo-root/
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .github/
│   └── workflows/
│       └── main.yml
├── tests/
│   ├── test_*.py
│   └── [additional test files]
└── [other application files as needed]
```

---

## SPECIFIC REQUIREMENTS SUMMARY

### ✓ Must Haves
1. ✓ Flask application (`app.py`) - functional and complete
2. ✓ Python dependencies file (`requirements.txt`)
3. ✓ Git repository initialized locally
4. ✓ GitHub repository (publicly accessible)
5. ✓ Pytest test suite with meaningful coverage
6. ✓ Dockerfile (functional and optimized)
7. ✓ GitHub Actions workflow (`.github/workflows/main.yml`)
8. ✓ Working Jenkins BUILD configuration
9. ✓ Professional README.md documentation
10. ✓ All three CI/CD pipeline stages implemented

### ✓ Quality Standards
- Meaningful Git commit history
- Comprehensive test coverage
- Optimized Docker image
- Reliable and consistent pipeline execution
- Professional documentation
- Industry-standard naming conventions

---

## SUBMISSION REQUIREMENTS

- **Format:** GitHub Repository Link (publicly accessible)
- **Contents:** All deliverables as specified above
- **Accessibility:** Public repository (verified access from external sources)
- **Documentation:** Complete README.md with all required sections

---

## KEY LEARNING OUTCOMES

Upon completion of this assignment, students will have demonstrated:
1. Proficiency with Flask web application development
2. Mastery of Git/GitHub version control
3. Expertise with Docker containerization
4. Understanding of CI/CD principles and automation
5. Ability to integrate Jenkins and GitHub Actions
6. Competence in automated testing (Pytest)
7. Professional DevOps engineering practices
8. Infrastructure as Code (IaC) fundamentals

---

**Document Generated:** April 2, 2026  
**Extracted From:** Introduction to DevOps Assignment - 1 2026.docx
