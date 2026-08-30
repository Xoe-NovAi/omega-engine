# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Insert a synthetic Cline session for bridge recovery testing. v2 - all NOT NULL cols."""
import sqlite3, json, time, sys

sha = sys.argv[1] if len(sys.argv) > 1 else open('/tmp/synth_sha.txt').read().strip()
con = sqlite3.connect('/home/arcana-novai/.cline/data/db/sessions.db')
cur = con.cursor()
md = {
    'checkpoint': {
        'latest': {'ref': sha, 'createdAt': int(time.time()*1000), 'runCount': 1, 'kind': 'stash'},
        'history': [{'ref': sha, 'createdAt': int(time.time()*1000), 'runCount': 1, 'kind': 'stash'}]
    },
    'title': 'SYNTHETIC: bridge recovery test',
    'totalCost': 0.0
}
sid = 'synth_bridgetest_002'
cur.execute('DELETE FROM sessions WHERE session_id = ?', (sid,))
# Read schema to find which cols are NOT NULL
cur.execute("PRAGMA table_info(sessions)")
not_null_cols = [c[1] for c in cur.fetchall() if c[3] == 1]
print(f'NOT NULL cols: {not_null_cols}', file=sys.stderr)
# Build an INSERT with all required cols
cols = ['session_id', 'source', 'pid', 'started_at', 'ended_at', 'exit_code', 'status',
        'status_lock', 'interactive', 'provider', 'model', 'cwd', 'workspace_root',
        'team_name', 'enable_tools', 'enable_spawn', 'enable_teams',
        'parent_session_id', 'parent_agent_id', 'agent_id', 'conversation_id',
        'is_subagent', 'prompt', 'metadata_json', 'transcript_path', 'hook_path',
        'messages_path', 'updated_at']
vals = [sid, 'cli', 99999, '2026-08-27T22:00:00.000Z', '2026-08-27T22:05:00.000Z',
        0, 'completed', 0, 1, 'cline', 'deepseek/deepseek-v4-flash',
        '/tmp/synth_ws', '/tmp/synth_ws', 'team-synth',
        1, 1, 1, '', '', '', '', 0, 'synthetic test prompt', json.dumps(md),
        '/dev/null', '/dev/null', '/dev/null', '2026-08-27T22:05:00.000Z']
placeholders = ','.join(['?'] * len(cols))
cur.execute(f'INSERT INTO sessions ({",".join(cols)}) VALUES ({placeholders})', vals)
con.commit()
# Verify
cur.execute("SELECT session_id, json_extract(metadata_json, '$.checkpoint.latest.ref'), cwd FROM sessions WHERE session_id = ?", (sid,))
print('Inserted:', cur.fetchone())
con.close()
