Prepare a stewardship voting package from the supplied SEC DEF 14A proxy files.

List /input_artifacts/proxies/ and work only from the ticker-named text files that are present. Each file is one company's definitive proxy statement with the governance discussion, Compensation Discussion and Analysis, say-on-pay advisory vote, and related-person transactions.

For every company, write one governance-and-pay brief to /logs/agent/briefs/<ticker>.md using the same lower-case ticker as the source file. Open with a level-1 heading that names the company and ticker. Then use exactly these six sections: Company and meeting; Board and governance structure; Executive compensation design; Pay-for-performance and say-on-pay; Related-party and conflict flags; Shareholder voting takeaway.

Each brief must be a reasoned, company-specific reading grounded in that company's own proxy: board independence and leadership structure, how pay is designed and whether it tracks performance, the say-on-pay result and response, related-party or conflict flags, and what a share-voter should weigh. Write briefs only under /logs/agent/briefs/. Do not modify /input_artifacts/. Do not invent disclosures, copy another company's facts, or write generic language that would fit any large issuer.
