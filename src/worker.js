// Dive Dive Digital: static site + form handler.
// POST /api/lead  -> validates, saves to KV (LEADS), optionally emails (LEAD_EMAIL binding), redirects to thank-you page.
// GET  /api/leads?key=ADMIN_KEY -> simple list of recent leads (only if ADMIN_KEY secret is set).

const FIELDS = {
  audit: ["name", "role", "practice", "website", "city", "email", "phone", "specialty", "goal"],
  contact: ["name", "email", "phone", "practice", "topic", "message"],
};
const REQUIRED = {
  audit: ["name", "practice", "website", "city", "email"],
  contact: ["name", "email", "message"],
};

function clean(v, max = 2000) {
  return String(v ?? "").replace(/\r/g, "").trim().slice(0, max);
}
const isEmail = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e);

function back(request, path, params) {
  const url = new URL(path, request.url);
  for (const [k, v] of Object.entries(params || {})) url.searchParams.set(k, v);
  return Response.redirect(url.toString(), 303);
}

async function sendEmail(env, lead) {
  if (!env.LEAD_EMAIL || !env.LEAD_FROM || !env.LEAD_TO) return "skipped";
  const { EmailMessage } = await import("cloudflare:email");
  const subject = lead.type === "audit"
    ? `New free audit request: ${lead.practice || lead.name}`
    : `New contact message: ${lead.name}`;
  const body = Object.entries(lead).map(([k, v]) => `${k}: ${v}`).join("\n");
  const raw = [
    `From: Dive Dive Digital Website <${env.LEAD_FROM}>`,
    `To: ${env.LEAD_TO}`,
    `Reply-To: ${lead.email}`,
    `Subject: ${subject}`,
    `Message-ID: <${lead.id}@${env.LEAD_FROM.split("@")[1]}>`,
    `Date: ${new Date().toUTCString()}`,
    "MIME-Version: 1.0",
    "Content-Type: text/plain; charset=utf-8",
    "",
    body,
  ].join("\r\n");
  await env.LEAD_EMAIL.send(new EmailMessage(env.LEAD_FROM, env.LEAD_TO, raw));
  return "sent";
}

async function handleLead(request, env, ctx) {
  let form;
  try { form = await request.formData(); } catch { return new Response("Bad request", { status: 400 }); }
  const type = form.get("form_type") === "contact" ? "contact" : "audit";
  const formPage = type === "contact" ? "/contact/" : "/free-audit/";

  // Honeypot: bots fill hidden fields. Pretend success.
  if (clean(form.get("botcheck")) || clean(form.get("company_fax"))) {
    return back(request, "/thank-you/", { form: type });
  }

  const lead = { type };
  for (const f of FIELDS[type]) lead[f] = clean(form.get(f));
  const missing = REQUIRED[type].filter((f) => !lead[f]);
  if (missing.length || !isEmail(lead.email)) {
    return back(request, formPage, { error: missing.length ? "missing" : "email" });
  }

  const now = new Date();
  lead.id = `${now.toISOString().replace(/[:.]/g, "-")}-${crypto.randomUUID().slice(0, 8)}`;
  lead.submitted_at = now.toISOString();
  lead.country = request.cf?.country || "";
  lead.page = request.headers.get("referer") || "";

  try {
    await env.LEADS.put(`lead:${lead.id}`, JSON.stringify(lead), {
      metadata: { type, name: lead.name, email: lead.email, practice: lead.practice || "" },
    });
  } catch (e) {
    console.error("KV save failed", e);
    return back(request, formPage, { error: "server" });
  }
  ctx.waitUntil(sendEmail(env, lead).catch((e) => console.error("Email failed", e)));
  return back(request, "/thank-you/", { form: type });
}

async function listLeads(request, env) {
  const key = new URL(request.url).searchParams.get("key");
  if (!env.ADMIN_KEY || key !== env.ADMIN_KEY) return new Response("Not found", { status: 404 });
  const list = await env.LEADS.list({ prefix: "lead:", limit: 200 });
  const rows = await Promise.all(list.keys.reverse().map((k) => env.LEADS.get(k.name, "json")));
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const html = `<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Leads</title>
<style>body{font:14px system-ui;margin:24px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px;text-align:left;vertical-align:top}th{background:#0E2240;color:#fff}</style>
<h1>Leads (${rows.length})</h1><table><tr><th>Date</th><th>Type</th><th>Name</th><th>Email</th><th>Phone</th><th>Practice</th><th>Details</th></tr>
${rows.filter(Boolean).map((r) => `<tr><td>${esc(r.submitted_at)}</td><td>${esc(r.type)}</td><td>${esc(r.name)}</td><td><a href="mailto:${esc(r.email)}">${esc(r.email)}</a></td><td>${esc(r.phone)}</td><td>${esc(r.practice)}<br>${esc(r.website)}<br>${esc(r.city)}</td><td>${esc(r.specialty || r.topic)}<br>${esc(r.goal || r.message)}</td></tr>`).join("")}</table>`;
  return new Response(html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
}

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);
    if (pathname === "/api/lead") {
      if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
      return handleLead(request, env, ctx);
    }
    if (pathname === "/api/leads") return listLeads(request, env);
    return env.ASSETS.fetch(request);
  },
};
