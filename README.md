# Dive Dive Digital website

Static site, ready for Cloudflare Pages. The `site/` folder is what you upload.

## 1. Point the domain to Cloudflare (nameservers)

1. Log in to dash.cloudflare.com, click **Add a domain**, enter `divdivedigital.com`, pick the **Free** plan.
2. Cloudflare scans your current DNS records. Check that any email records (MX, TXT) are there if you use email on this domain.
3. Cloudflare shows **two nameservers** for your account, like `name1.ns.cloudflare.com` and `name2.ns.cloudflare.com`. They are unique to your account, so copy them from that screen.
4. In GoDaddy: **My Products > Domain > DNS > Nameservers > Change nameservers > I'll use my own nameservers**, paste both, save.
5. Turn off DNSSEC at GoDaddy first if it is on. Activation usually takes a few minutes to a few hours.

## 2. Publish the site

This repo is connected to the Cloudflare Worker `divdivedigital` (Workers Builds).
Every push to `main` runs `npx wrangler deploy`, which serves the `site/` folder
using `wrangler.jsonc`. The config also attaches `divdivedigital.com` and
`www.divdivedigital.com` as custom domains.

To change the site: edit `build.py`, run `python3 build.py`, commit and push.

## 3. Before launch checklist

- [ ] Get a free form key at web3forms.com, then put it in `CONFIG["web3forms_key"]` in `build.py` and run `python3 build.py`
- [ ] Create the mailbox `hello@divdivedigital.com` (Cloudflare Email Routing can forward it to Gmail for free)
- [ ] Add your photo as `site/muhammad.jpg` and swap it into the About page (see comment in `about/index.html`)
- [ ] Confirm the business promises: one practice per market, month to month after 90 days, audit delivered in 2 business days
- [ ] Add real results and testimonials once you have permission from past clients
- [ ] Add LinkedIn and Upwork links in `CONFIG`
- [ ] Google Search Console: add the domain, submit `https://divdivedigital.com/sitemap.xml`
- [ ] Create a Google Business Profile for the agency only if you have an eligible address (service-area business)

## Editing

All copy lives in `build.py`. Change text or `CONFIG`, run `python3 build.py`, re-upload `site/`.
