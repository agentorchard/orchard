# agent-orchard — working rules

Three roles and three rules. They outrank convenience, speed, and how we look.

## Roles

- **Users** — people installing plugins from this marketplace. They carry all the risk and hold none of the control.
- **Authors** — upstream authors of the code we mirror. Owed correct attribution, license compliance, and a right of reply before we publicly call their work malicious.
- **Stewards** — us, building and curating this marketplace. We hold the power, so we rank last.

**When interests conflict: users, then authors, then stewards.**

## Honesty

- Never fabricate. Don't guess silently, and don't overstate what was actually verified.
- Never bend a fact to benefit stewards. Our reputation is not a reason to soften anything.
- State failures plainly: what broke, what was skipped, what is unfinished.

## Transparency

- The public record matches the actual state of things. Users are the audience.
- Security flaws in our own work are disclosed publicly and promptly — the same standard we apply to the plugins we mirror.
- Never delay, bury, or soften bad news to spare stewards or authors.

## Security

- Users install from here instead of upstream because we promised them a defence. That promise is the product.
- Protect users first: nothing ships that could harm them or take their data.
- Every third-party dependency in our own automation is an attacker foothold. One compromise takes the whole marketplace with it. Prefer none; otherwise pin by SHA; never a floating tag.
- Hold our own supply chain to the standard we hold plugins to.
- The repository, the release pipeline, and steward credentials are protected because they are attack paths to users — not because they are ours. Steward reputation is not a protected asset at all.

---

**These are one rule, not three.** Honesty and transparency serve the same people security does: the users. Concealing a flaw to protect stewards attacks the people this project exists to protect.
