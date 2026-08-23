TICKET-4821 — "Checkout broken?? (urgent-ish)"

Reporter: @dana
Created: 3 days ago

So since the v14 deploy sometimes checkout just spins. Not always?? Mostly when the cart has more than like 20 items, someone said maybe on Safari too but unconfirmed.

Comments:
@priya: I saw this too on staging. We think it might be the pricing service timeout. Or the new tax table? Dana changed the tax table.
@dana: FYI I did NOT touch pricing. The tax table change is here: https://git.internal/tax-table-pr-4712 (merged in v14). It only adds a lookup for EU countries.
@sam (QA): reproduced on staging: cart with 25 items -> spinner >30s, then order still goes through eventually. Cart with 5 items -> fine. Network tab shows /api/checkout taking ~31s when it happens.
@priya: also we got an alert that pricing-service p99 latency tripled after v14, probably unrelated but mentioning it.

Acceptance criteria (buried down here, sorry):
- checkout with large carts completes without the spinner timing out
- if the pricing service is slow, checkout should not hang waiting on it

Slack thread continues in #checkout-firefight. Also please update the API docs page with whatever we decide, and while you're in there can you also migrate the docs to the new template? And rename the checkout service to "order-engine"? That last one is just me thinking out loud, ignore if it's dumb.
