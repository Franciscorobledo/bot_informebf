-- PostgreSQL-ready schema for multi-tenant SaaS booking bots

create table tenants (
  id uuid primary key,
  name text not null,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table bots (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  name text not null,
  system_prompt text not null,
  features jsonb not null default '{}'::jsonb,
  slack_team_id text not null,
  slack_channel_id text not null,
  google_calendar_id text not null,
  created_at timestamptz not null default now()
);

create unique index bots_slack_channel_unique
  on bots (slack_team_id, slack_channel_id);

create table bot_rules (
  id uuid primary key,
  bot_id uuid not null references bots(id),
  rule_type text not null,
  rule_payload jsonb not null,
  created_at timestamptz not null default now()
);

create table conversation_sessions (
  id uuid primary key,
  bot_id uuid not null references bots(id),
  slack_user_id text not null,
  state text not null,
  context_json jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create unique index conversation_sessions_unique
  on conversation_sessions (bot_id, slack_user_id);

create table appointments (
  id uuid primary key,
  bot_id uuid not null references bots(id),
  slack_user_id text not null,
  service text not null,
  start_time timestamptz not null,
  end_time timestamptz not null,
  google_event_id text,
  created_at timestamptz not null default now()
);

create table integrations (
  id uuid primary key,
  tenant_id uuid not null references tenants(id),
  provider text not null,
  access_token text not null,
  refresh_token text,
  expires_at timestamptz,
  created_at timestamptz not null default now()
);

