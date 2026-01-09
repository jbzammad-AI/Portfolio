# ESL Study Plan Engine

**Personalised ESL study plan generator with weekly calendar, skill progress bars, and AI explanations.**

---

## Overview

This project generates **personalised ESL study plans** for learners based on:

- Learner skills and weak points
- Exam dates
- Product type (Standard, Pro, Pro Max)
- Learning history

Outputs include:

- **HTML**: browser-ready weekly study plans  
- **JSON**: API-ready structured plans  
- **AI explanations**: short text showing why each lesson matters  

Supports **batch processing** for thousands of learners.

---

## Features

- Rule-based lesson selection
- Weekly calendar layout for easy tracking
- Skill progress bars for visual feedback
- AI explanations for each lesson (OpenAI GPT optional)
- FastAPI endpoint for API access
- Easy to extend for different product types

---

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
