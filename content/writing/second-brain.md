---
title: Build a Second Brain
tags:
  - ai
  - productivity
description: How I wired Claude into my actual work tools, packaged my recurring workflows as skills, and gave it a persistent memory of who I am.
---

A single prospect in my pipeline might have history across the CRM, a recent email thread, a WhatsApp conversation, call notes, and a Slack message from someone on the buying team. Getting oriented before reaching out meant opening all of those tabs and reading backwards through time. The kind of task that never felt important enough to do properly, but where skipping it had a real cost.

The same problem showed up after sales trips. Come back, face an evening of writing follow-ups from scratch, updating CRM stages, filing notes. The quality of those follow-ups correlated directly with how tired I was.

I work in GTM. This kind of admin is the gap between the actual job and everything the actual job requires. I started wondering whether it was possible to wire AI properly into the work, rather than treating it as a separate tool I switched between.

## Karpathy's idea

Andrej Karpathy published a [gist in early 2025](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) describing what he called an LLM wiki. The core observation: the reason most personal knowledge bases fail is maintenance. Humans build them, then stop updating them, because the bookkeeping is tedious. An LLM doesn't get bored.

His system has three parts. A raw folder where you dump unorganized source material: articles, transcripts, notes, anything. A wiki where the LLM compiles and maintains structured knowledge, building concept pages, entity pages, summaries, and a navigation index. A schema file that defines what the knowledge domain looks like and how the wiki should update itself.

AI is well-suited to the maintenance work humans consistently abandon. Separating ingestion from structure means you can keep adding to the system without having to reorganize it.

I read that and thought about what the same pattern would look like wired into real work tools, where the context already lives.

## What I built

The result is a system with five layers sitting on top of Claude.

**Connectors** are live, authenticated links into the tools where my work actually lives. For my role, that means Attio (my CRM), Gmail and Google Calendar, Slack, WhatsApp, Granola and Fireflies for meeting notes and call transcripts, Sprout Social, BigQuery and Metabase for the data warehouse, Shopify, and Notion. The system can read from and act in all of them. I didn't build any of these; I composed them.

**Memory** is my version of Karpathy's wiki. A curated set of markdown files covering who I am, who my customers are, how I like messages written, and the reasoning behind recurring decisions. There's an index file, topic files, and a consolidation routine that periodically merges duplicates, retires stale notes, and converts vague timestamps into real dates. The discipline is keeping it for things that are hard to re-derive. If a connector can fetch a fact fresh, it doesn't belong in memory.

**Skills** are packaged, repeatable workflows triggered in plain language.

**Automation** is scheduled tasks that run without me asking, plus live dashboards that re-pull data from connectors each time I open them.

**The reasoning core** is Claude, orchestrating everything: deciding which tools to call, in what order, writing the output, and checking its own work.

![The second brain in layers: a reasoning core that orchestrates connectors into my real tools, a library of packaged workflows (skills), a persistent memory, and automation that runs on its own.](/assets/second-brain-architecture.png)

## The skills are where the leverage is

There are two kinds of skills in the setup. Off-the-shelf skills cover the standard surface area: document creation, presentation building, call prep and summaries, analytics against the data warehouse. Useful, but not what makes this feel different.

The bespoke skills are the real thing. Each one is a procedure I wrote down for my exact job.

**Pipeline digest** pulls my Attio leads every morning, groups them by deal stage, and gives me a concrete next action per lead before I've opened anything else.

**Post-visit follow-up** finds everyone I met in person in a given time window, reads what each one sells from their CRM record, and drafts a WhatsApp message and email for each in my voice, referencing what we actually talked about.

**Follow-up generator** does the same for a single named lead: reads their stage, our message history, what they sell, and drafts the next touch on whichever channel I specify.

**Vintage store profiler** takes a store's website or Instagram handle and returns their aesthetic, price points, customer profile, and a specific angle for why we fit. Research that used to take twenty minutes takes thirty seconds.

**Customer feedback digest** pulls signal from meeting notes, the team Slack channel, and the social inbox every two weeks into a themed voice-of-customer report for marketing and product, with quotes.

The pattern across all of them: take something I was doing repeatedly, write the procedure down once, and make it a one-liner. The cost of building a new skill is mostly the cost of articulating steps I was already doing manually.

## How a day actually runs

Morning. I ask for the pipeline digest. The system reads Attio and hands me a prioritized list with a next action per lead. A scheduled task has already swept overnight Instagram DMs and updated the relevant stages. I'm oriented before I've opened anything else.

After a sales trip. "Do my post-visit follow-ups." The system finds everyone I met in the last week, reads their records, and drafts a WhatsApp and email for each in my voice. I go through them, make edits, send. What used to be an evening of writing is fifteen minutes of reviewing.

Chasing one prospect. "Follow up with [store]." It reads their stage, our history, and what they sell, then drafts the next message on the right channel. No tab-hopping, no re-reading the thread first.

![How one request flows through the system: a plain-language ask becomes a sequence of tool calls, and comes back as a finished draft, with me only in the loop for judgment.](/assets/second-brain-workflow.png)

The system does the gathering and the first draft. I do the judgment and the relationship.

## What changed

I won't dress this up with invented numbers. The qualitative shift is clear enough.

The admin that used to fill the gaps in my day is mostly gone. Follow-ups, CRM updates, and reporting are now minutes of reviewing rather than hours of doing. Fewer leads go cold because context gets assembled automatically rather than depending on whether I have time to reconstruct it from scratch. Every session starts oriented because memory and connectors do that work before I ask.

The compounding effect was the part I didn't expect. Every new skill makes the next task cheaper. Every memory update means one less thing to re-explain. The system gets more useful the longer I use it, which is not how most tools work.

![Same job, two days. Before: scattered tabs and an evening of admin. After: a one-line request and fifteen minutes of review.](/assets/second-brain-before-after.png)

## What I learned

**Compose, don't build.** The value came from connecting tools that already existed and teaching the system how to use them together. The connectors were there. The AI was there. The work was the wiring.

**Name your repetitions.** Karpathy's observation about wiki maintenance applies to skills too. If you do something three times, writing the procedure down once is most of the work. The barrier to building a new skill is lower than it looks.

**Memory is for what's hard to re-derive.** Store preferences and the reasoning behind decisions. Let connectors fetch the facts. Keeping memory tight is what stops the system from becoming noise over time.

**Keep it pruned.** This is the part of Karpathy's pattern people tend to underweight. A knowledge base that isn't maintained becomes a liability faster than you'd think. The consolidation routine is load-bearing.

I stopped using AI as a tool I opened when I needed help and started treating it as infrastructure I configured. The leverage comes from the assembly, not any individual prompt.

## Honest caveats

Every outbound message gets reviewed before it goes anywhere. The system drafts; I approve. That's deliberate, and I wouldn't change it.

Setup takes time. The first few skills are the hardest because you're figuring out the pattern. After that, new ones are cheap. The connectors require real configuration and authentication. There's a genuine upfront cost before the returns start.

The system is only as good as the data underneath it. A messy CRM produces a messy digest. Building this made the quality of my underlying data matter in a way it hadn't before.

And it's shaped around one job, one set of tools, one set of repeated workflows. The components are general. The value comes from tailoring. Start by identifying the three things you do most often that are really just procedures, and write them down.
