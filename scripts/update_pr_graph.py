#!/usr/bin/env python3
"""Draw RITU940's *real* GitHub PR history as a local SVG.

The normal command requires GITHUB_TOKEN. `--placeholder` makes a truthful
initial graphic; `--demo` only writes a preview, clearly watermarked SAMPLE.
No runtime dependencies beyond Python's standard library.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import sys
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
PREVIEW = ROOT / 'preview'
USER = 'RITU940'
BG = '#f6f1e6'
INK = '#20342a'
GREEN = '#687e62'
RUST = '#c78360'
MUTED = '#6b7468'
RULE = '#d9d5c7'

GQL = '''query($q: String!, $after: String) {
 search(query: $q, type: ISSUE, first: 100, after: $after) {
  issueCount
  pageInfo { hasNextPage endCursor }
  nodes {
   ... on PullRequest {
    id url createdAt mergedAt repository { nameWithOwner }
   }
  }
 }
}'''


def e(value) -> str:
    return html.escape(str(value), quote=True)


def first_month(date: dt.date) -> dt.date:
    return date.replace(day=1)


def minus_months(day: dt.date, n: int) -> dt.date:
    key = day.year * 12 + day.month - 1 - n
    return dt.date(key // 12, key % 12 + 1, 1)


def months_last_year(today: dt.date) -> list[str]:
    return [minus_months(first_month(today), 11 - i).strftime('%Y-%m') for i in range(12)]


def graphql(token: str, query: str, after: str | None):
    body = json.dumps({'query': GQL, 'variables': {'q': query, 'after': after}}).encode('utf-8')
    req = urllib.request.Request(
        'https://api.github.com/graphql', data=body,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'User-Agent': 'RITU940-profile-pr-graph',
            'X-GitHub-Api-Version': '2022-11-28',
        }, method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.load(r)
    except urllib.error.HTTPError as ex:
        raise RuntimeError(f'GitHub API returned HTTP {ex.code}. Chart left unchanged.') from ex
    if data.get('errors'):
        raise RuntimeError('GitHub GraphQL returned an error. Chart left unchanged: ' +
                           '; '.join(str(x.get('message', 'unknown')) for x in data['errors']))
    return data['data']['search']


def search_prs(token: str, query: str) -> list[dict]:
    all_nodes, cursor = [], None
    while True:
        result = graphql(token, query, cursor)
        if result['issueCount'] > 1000:
            raise RuntimeError('GitHub search would truncate more than 1000 PRs. Split query into shorter date ranges before publishing.')
        nodes = [n for n in result['nodes'] if n and n.get('createdAt')]
        all_nodes.extend(nodes)
        page = result['pageInfo']
        if not page['hasNextPage']:
            break
        cursor = page['endCursor']
        if not cursor or len(all_nodes) >= 1000:
            raise RuntimeError('Pagination incomplete; chart left unchanged.')
    if len(all_nodes) < result['issueCount']:
        raise RuntimeError('Search returned fewer PRs than reported; chart left unchanged.')
    return all_nodes


def aggregate(opened: list[dict], merged: list[dict], months: list[str]) -> dict:
    created = {k:0 for k in months}
    fused = {k:0 for k in months}
    repo_names = set()
    seen_created = set()
    seen_merged = set()
    for pr in opened:
        ident = pr['id']
        key = pr['createdAt'][:7]
        if key in created and ident not in seen_created:
            created[key] += 1
            seen_created.add(ident)
            if pr.get('repository'):
                repo_names.add(pr['repository']['nameWithOwner'])
    for pr in merged:
        ident = pr['id']
        merged_at = pr.get('mergedAt')
        if merged_at is None:
            raise ValueError('GitHub returned a supposedly merged PR without mergedAt')
        key = merged_at[:7]
        if key in fused and ident not in seen_merged:
            fused[key] += 1
            seen_merged.add(ident)
            if pr.get('repository'):
                repo_names.add(pr['repository']['nameWithOwner'])
    return {'months':months, 'opened':created, 'merged':fused, 'repos':len(repo_names)}


def element_text(x,y,s,size=14,color=INK,weight=400,anchor='start',mono=False):
    family = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace' if mono else 'Arial, Helvetica, sans-serif'
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{e(s)}</text>'


def svg_chart(data: dict | None, updated: str, demo: bool=False) -> str:
    w,h=1000,328
    a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Pull requests opened and merged by month over the past year">',
       f'<rect width="{w}" height="{h}" fill="{BG}"/>',
       '<path d="M9 9H991V319H9Z" fill="none" stroke="#c4c4b3" stroke-width="2"/>',
       '<path d="M21 21H979V307H21Z" fill="none" stroke="#e4dfd4" stroke-width="1"/>',
       element_text(48,54,'gh search prs --author RITU940',16,INK,600,mono=True),
       element_text(48,81,'PULL REQUESTS  /  LAST 12 MONTHS',13,MUTED,600,mono=True),
       '<rect x="49" y="101" width="11" height="11" fill="'+GREEN+'"/>',element_text(66,111,'opened',12,INK),
       '<rect x="142" y="101" width="11" height="11" fill="'+RUST+'"/>',element_text(159,111,'merged',12,INK)]
    if data is None:
        for i in range(12):
            x=82+i*73
            a += [f'<rect x="{x}" y="191" width="22" height="83" fill="none" stroke="{GREEN}" stroke-dasharray="3 5"/>',
                  f'<rect x="{x+27}" y="218" width="22" height="56" fill="none" stroke="{RUST}" stroke-dasharray="3 5"/>']
        a += [f'<rect x="230" y="150" width="540" height="80" fill="{BG}" stroke="{INK}" stroke-width="2"/>',
              element_text(500,181,'no made-up numbers here.',18,INK,700,'middle',mono=True),
              element_text(500,210,'Run Actions > Update PR graph once to fetch real history.',12,MUTED,400,'middle')]
    else:
        dates=data['months']
        op=[data['opened'].get(m,0) for m in dates]
        mg=[data['merged'].get(m,0) for m in dates]
        y_bottom=272
        y_top=135
        maximum=max(2,max(op+mg))
        top=math.ceil(maximum/2)*2
        for j in range(3):
            y=y_bottom-(y_bottom-y_top)*j/2
            a.append(f'<line x1="63" y1="{y:.1f}" x2="948" y2="{y:.1f}" stroke="{RULE}" stroke-width="1"/>')
            a.append(element_text(51,round(y+4,1),str(round(top*j/2)),11,MUTED,anchor='end',mono=True))
        for i,m in enumerate(dates):
            x=82+i*73.0
            for k,(value,color) in enumerate(((op[i],GREEN),(mg[i],RUST))):
                bar=(value/top)*(y_bottom-y_top)
                if value:
                    a.append(f'<rect x="{x+26*k:.1f}" y="{y_bottom-bar:.2f}" width="18" height="{bar:.2f}" fill="{color}"/>')
            month=dt.date.fromisoformat(m+'-01').strftime('%b').lower()
            a.append(element_text(round(x+22,1),292,month,12,MUTED,500,'middle',mono=True))
            if m.endswith('-01') or i==0:
                a.append(element_text(round(x+22,1),307,m[:4],9,MUTED,400,'middle',mono=True))
        total_op=sum(op);total_mg=sum(mg)
        a += [element_text(685,55,f'{total_op} opened',19,GREEN,700),
              element_text(838,55,f'{total_mg} merged',19,RUST,700),
              element_text(687,79,f'{data["repos"]} repositories',11,MUTED,500,mono=True)]
    a.append(element_text(945,114,('sample data / design preview' if demo else 'current through '+updated),10,MUTED,400,'end',mono=True))
    if demo:
        a.append(f'<rect x="342" y="124" width="326" height="36" fill="{BG}" stroke="{RUST}" stroke-width="2"/>')
        a.append(element_text(505,148,'SAMPLE DATA — NOT REAL PR COUNTS',13,RUST,700,'middle',mono=True))
    a.append('</svg>')
    return '\n'.join(a)


def main() -> None:
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group()
    g.add_argument('--placeholder',action='store_true')
    g.add_argument('--demo',action='store_true')
    args=p.parse_args()
    months=months_last_year(dt.datetime.now(dt.timezone.utc).date())
    if args.placeholder:
        ASSETS.mkdir(exist_ok=True)
        (ASSETS/'pull-requests.svg').write_text(svg_chart(None, ''),encoding='utf-8')
        print('Wrote a placeholder with no invented activity data.')
        return
    if args.demo:
        sample_o=[0,1,3,2,1,4,3,6,2,4,5,2]
        sample_m=[0,0,1,1,1,2,1,3,1,2,4,1]
        data={'months':months,'opened':dict(zip(months,sample_o)), 'merged':dict(zip(months,sample_m)),'repos':4}
        PREVIEW.mkdir(exist_ok=True)
        (PREVIEW/'pr-graph-SAMPLE.svg').write_text(svg_chart(data,'sample',True),encoding='utf-8')
        return
    token=os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN is required. Use --demo for sample artwork.')
    first=months[0]+'-01'
    opened=search_prs(token, f'is:pr author:{USER} created:>={first}')
    merged=search_prs(token, f'is:pr author:{USER} is:merged merged:>={first}')
    data=aggregate(opened,merged,months)
    updated=dt.datetime.now(dt.timezone.utc).strftime('%b %Y')
    text=svg_chart(data,updated)
    ASSETS.mkdir(exist_ok=True)
    # The file is only written when *all* GitHub pages loaded successfully.
    (ASSETS/'pull-requests.svg').write_text(text,encoding='utf-8')
    print(f'Updated PR chart: {sum(data["opened"].values())} opened, {sum(data["merged"].values())} merged, across {data["repos"]} repositories.')

if __name__=='__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError) as exc:
        print('error:',str(exc),file=sys.stderr)
        sys.exit(1)
