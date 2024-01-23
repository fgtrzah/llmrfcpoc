#### Overview

The work in progress backend for [rfcindex frontend](https://github.com/fgtrzah/rfcllmpoc1). RFC Index is 
a simple poc of a system that leverages ietf datatracker api + tooling to facilitate *keyword 
search* over 9000+ RFC documents. At its core it explores basic use cases of prompt engineering - might expand
in the future. Time permitting, a full roadmap or detailed series might be dedicated to document its evolution as I think of use cases or
useful functionality. But the tldr: this is a gentle primer into using commonly known llm apis to facilitate 
exploration and comprehension of RFC documents.

*aside:* definitely not suitable as a boilerplate or starting point for production genai pipelines or projects, so fork
at your own potential peril / disgretion.

#### Requiremnets

- OpenAI API Key

#### Optional

- Auth0 configuration (this is easily removable and not central to most of the endpoints)

#### Setup & local development

You can run local builds via most python virtualization tools and a set of metadata
for scaffolding with necessary secrets/config params.

1. ```cp .env.example .env``` and then step through and substitute as needed. The settings
module under ```config/settings.py``` is self documenting and offers good indications of 
necessary / optional environment variables
2. ```python -m venv .venv && source .venv/bin/activate```
3. ```pip install -r requirements.txt```
4. ```uvicorn main:app --reload``` or configure uvicorn programmatically inside an ifmain
block in `main.py` and then ```python main.py```

#### Credits / Inspo

- [instructor](https://jxnl.github.io/instructor/)
- whoever wrote the first RFC (idrk)
- whoever decided how they'd 
  be formatted (cheff's kiss)

#### Roadmap

- moderation api endpoint usage for taming hallucinations
- monitoring the egress/entry points attached to the parts
of code interfacing with api response + interfacing with OpenAI
requests
- hard requirements: trace all dataflow to OpenAI whois info 
and stow in sqlite while linking to currently authenticated user's
id
- toxicity detection and phonetic vulgarity filtering
- controlled chaos prevention
- draft t.o.s that is succinct and clearly emphasizes all data
that is idempotently associable to the current user - ensure 0
chance of liability and full transparency
- trust but verify exhaustively
- sanitize inputs (utilize a moderation dto layer for the no brainer 
injection prevention needs)

#### MISC

- some fake keys can be found in lfs / I was testing code analysis using codeql to 
come up with a sensible security policy / bolster code quality
- feedback and prs are always welcome
