# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Insert a synthetic Cline session for bridge recovery testing."""
import sqlite3, json, time
con = sqlite3.connect('/home/arcana-novai/.cline/data/db/sessions.db')
cur = con.cursor()
sha = 'ac5826f97c2352556d3d7b7272f52dfb04bf2b20'
md = {
    'checkpoint': {
        'latest': {'ref': sha, 'createdAt': int(time.time()*1000), 'runCount': 1, 'kind': 'stash'},
        'history': [{'ref': sha, 'createdAt': int(time.time()*1000), 'runCount': 1, 'kind': 'stash'}]
    },
    'title': 'SYNTHETIC: bridge recovery test',
    'totalCost': 0.0
}
sid = 'synth_bridgetest_001'
# Delete if exists, then insert
cur.execute('DELETE FROM sessions WHERE session_id = ?', (sid,))
cur.execute('''
    INSERT INTO sessions
    (session_id, source, pid, started_at, ended_at, exit_code, status, status_lock,
     interactive, provider, model, cwd, workspace_root, team_name,
     enable_tools, enable_spawn, enable_teams, parent_session_id, parent_agent_id,
     agent_id, conversation_id, is_subagent, prompt, metadata_json, transcript_path,
     hook_path, messages_path, updated_at)
    VALUES (?, 'cli', 99999, '2026-08-27T22:00:00.000Z', '2026-08-27T22:05:00.000Z',
            0, 'completed', 0, 1, 'cline', 'deepseek/deepseek-v4-flash',
            '/tmp/synthetic_workspace', '/tmp/synthetic_workspace', 'team-synth',
            1, 1, 1, NULL, NULL, NULL, NULL,             0, 'synthetic test prompt', ?,
            '/dev/null', '/dev/null', '/tmp/synthetic_workspace/synth_messages.json', '2026-08-27T22:05:00.000Z')
''', (sid, json.dumps(md)))
con.commit()
print(f'Inserted: {sid}')
# Verify
cur.execute("SELECT session_id, json_extract(metadata_json, '$.checkpoint.latest.ref'), cwd FROM sessions WHERE session_id = ?", (sid,))
print('Verify:', cur.fetchone())
con.close()
