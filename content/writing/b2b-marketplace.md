---
title: What I learned scaling a B2B marketplace from zero to $50m GMV
tags:
  - b2b
  - online-marketplace
  - startups
description: On supply constraints, commercial hiring, and the limits of disintermediation.
---

<div class="hero-image">
  <img src="/assets/container-ships.webp" alt="Container ship loaded with cargo">
</div>

Recycling sounds like it should be a growth industry. Mandates across the EU and UK are forcing manufacturers to incorporate recycled content into their products. Demand is structurally increasing, and yet over 90% of plastic never gets recycled. Mainly because the economics don't work. Virgin plastics are cheap, and recovering high-quality material from waste is costly, fragmented, and operationally painful.

That's the problem Safi was built to solve. Safi runs a marketplace for recycled materials such as plastics, metal, and paper, digitising what is still, in most parts of the world, a pen-and-paper process. Computer vision tools grade material quality on the spot. Integrated logistics handles the movement. Thoughtful automation replaces the endless phone calls and spreadsheets defining the industry today. The pitch was simple: better price discovery, more reliable supply, more liquid trading.

## Supply is the only thing that matters first

In consumer marketplaces, the conventional wisdom is demand is harder to build than supply. Aggregate enough buyers and suppliers will follow. B2B is often the opposite, but in our case it wasn't even symmetric. The recyclables industry is extremely supply-constrained. There's no excess availability sitting around waiting to be unlocked. Every tonne of material coming out of a materials recovery facility already has a buyer. Suppliers didn't need yet another channel.

This meant every supplier we onboarded was a genuine win. Not many suppliers came to Safi voluntarily to sell their material through us, so we had to go get them and convince people who had been doing business the same way for decades there was a better option. The instinct many marketplaces have, build the platform, create the network effects, and let the flywheel do the work, simply didn't apply.

## Building the commercial team

We hired both people who knew the market and people who knew how to build, and neither worked cleanly. The experienced industry hires were valuable in the early days of growing the marketplace business. They spoke the language of the industry. They had pre-existing relationships worth months or years of work. But getting them to operate like a startup was a pain. They often resisted the pace, the ambiguity, the willingness to do things differently. Their instinct was always to revert to how the industry had always worked, which defeated the point. We struggled to find an edge on the traditional brokers.

The junior generalists had the opposite problem. They moved fast and had no bad habits to unlearn. But the learning curve was steep and enthusiasm only takes you so far. Suppliers and buyers in this industry have decades of experience, so someone who can't get past a surface-level conversation about material grades isn't going to win their trust.

What I'd look for now, with the benefit of hindsight, is the person in the middle. Someone junior enough to still be malleable, but who has spent enough time around the industry to have real credibility in the room. They're harder to find, but they're the ones who compound over time.

## Cold outreach built volume. Referrals built trust

Our supply growth was almost entirely sales driven. Picking up the phones, cold emails, travelling to supplier sites and knocking on doors. Especially in markets where we had no critical mass, such as North Africa and Latin America, which turned out to be two of our strongest supply markets. Given the low conversion of direct sales, it only worked because of the volume of outreach we did.

Better pricing than other buyers was a weak pitch, because relationships run deep and switching costs exist. We sold growth instead: the ability to reach a global buyer network suppliers couldn't access before. Better payment terms. Cleaner logistics. A way to increase total throughput, not to optimise the margin on what they were already moving. That framing made a big difference.

Cold outreach alone didn't break the trust problem. These were often family businesses, some operating for multiple generations, so they were right to be suspicious of a new tech startup with no track record. We were the newcomers who, from their perspective, knew nothing.

Referrals solved this in a way cold outreach never could. We built a network of agents, mainly ex-industry folks with existing supplier relationships, who vouched for us in exchange for an introduction fee. When a well-respected industry veteran tells a supplier to trust you, the relationship starts from a very different place. It short-circuits the credibility problem every new marketplace faces in a traditional industry. If I were building again, I'd invest in that agent network earlier and more aggressively.

## Make the first transaction risk-free, then earn the relationship

Getting a supplier to transact with us for the first time was a fundamentally different problem from getting them to transact repeatedly. So we treated these as separate problems.

For first-time transactions, we subsidised the supply side. By offering better pricing than any of our offline competitors, we got our foot through the door and established a relationship with the supplier. It gave us the opportunity to provide an exceptional experience and earn the right to a second conversation.

It made sense because our unit economics justified it. The LTV of our suppliers was large enough relative to our CAC to justify losing money on the first transaction. Once a supplier had been through a transaction with us and seen the ease of doing business, the logistics reliability, and the overall experience, they came back. Often, repeat buyers who liked the material would pay a premium, which gave us room to be competitive on price in subsequent transactions without subsidising them indefinitely.

## Large AOV and high frequency can coexist in B2B. Monetising both is the hard part

In consumer marketplaces, you generally have to choose between high AOV (e.g. real estate) or high frequency (e.g. ride-hailing). B2B marketplaces break this rule. At Safi, our buyers were large manufacturers needing material consistently and in volume. Once we'd established supplier-buyer relationships, transactions were large and recurring. The question was how to capture value without a take rate becoming a visible disincentive to use the platform.

Our answer was a managed marketplace model. Rather than a standardised fee, we manually matched suppliers to buyers and negotiated pricing on both sides. Neither party had visibility into what the other was paying. Our margin on each transaction came from how well we worked the spread, which meant no ceiling on what we made on a well-matched deal. For a complex, opaque industry like recyclables trading, this made sense. The market wasn't efficient enough for transparent pricing to work yet.

The weakness showed up on the demand side. Our buyer base was more concentrated than we'd have liked. A small number of large manufacturers accounted for a disproportionate share of GMV. Buyers at scale have real leverage. They know their volume matters to you more than yours matters to them, so they push back on pricing and demand preferential terms. When demand is concentrated, the managed model's flexibility starts to work against you. We should have diversified the demand base earlier, even at the cost of some short-term GMV growth, which was difficult under investor pressure to grow GMV.

## The operations burden of a managed marketplace

A managed marketplace sounds more sophisticated than a traditional online marketplace (e.g. eBay). In some ways it is. The human judgment involved in matching, negotiating, and coordinating logistics produces better outcomes than an algorithm would in a market this complex. The downside is every transaction requires people, which means your operational headcount scales roughly in line with your GMV.

We started using AI to chip away at this. On the logistics side, we built automated workflows to parse shipping documents, match them against purchase orders, and flag discrepancies without someone manually cross-referencing spreadsheets. What had been a back-and-forth between our operations team and freight forwarders, emails, attachments, chasing confirmations, got compressed into something much closer to real time. On the matching side, we trained models on historical transaction data to surface the most likely buyer for a given parcel of material based on grade, geography, volume, and price history. It didn't replace the human decision, but it meant the person making the match was starting from a shortlist of two or three rather than scanning the entire buyer base from scratch.

The more interesting application was in quality grading. Safi AI, our computer vision tool, assessed material composition and condition from images taken at a supplier's facility. This meant we weren't relying entirely on supplier self-reporting or doing costly manual inspections for every transaction. It wasn't perfect, but it meaningfully reduced the number of quality claims we faced.

## Disrupting relationships you can't replace was the hardest part

Every B2B marketplace is, at some level, trying to replace a phone call. Something I underestimated going into this was how much B2B purchasing is built on personal relationships. Buyers in the recyclables industry had been working with the same suppliers for years, sometimes decades. They knew the quality of their material, they had payment terms working for both sides, and they had a person to call when something went wrong. We were asking them to move those transactions onto a platform run by people they'd never met. That's not a small ask.

The playbook most marketplaces follow is to try and disintermediate those relationships. Make the platform compelling enough buyers eventually route around their existing suppliers. I get the logic, but in practice it puts people on the defensive. You end up fighting the relationship rather than the inefficiency, which is a much harder battle.

What I'd do differently is try to bring existing relationships onto the platform rather than compete with them. If a buyer already has three suppliers they trust, help them manage those relationships better: visibility on orders, payment tracking, quality records. Become the place where their whole supply operation lives, not an alternative channel. The B2B marketplaces growing fastest were trying to sit on top of existing supplier relationships, not replace them. The transactions come eventually.
