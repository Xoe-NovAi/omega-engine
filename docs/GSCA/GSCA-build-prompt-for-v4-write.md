Everything is verified, solid, and fully hardened. We are clear to lift Plan Mode and move to execution. 

Please proceed with **Execution Mode A: Atomic Deployment**. Generate a single, comprehensive, production-grade bash deployment script (`deploy.sh`) that automates Phase 0 through Phase 11 sequentially. 

### Script Requirements & Guardrails:
1. **Multi-Node Deployment Strategy**: The script must generate a localized `deploy_node1.sh` for this machine (ASUS ExpertBook) and a separate `deploy_node0.sh` that can be easily scp'd and executed natively on the HP Pavilion archival bastion.
2. **Strict Verification Gates**: Implement an exit code check (`&&` or `if [ $? -ne 0 ]`) after every core step (directory creation, master `opencode.json` overwriting, systemd service deployment, and venv bootstrap checks). If any prerequisite check fails, halt execution immediately before changing runtime parameters.
3. **Automatic Systemd Unit Activation**: Ensure the script reloads the user systemctl manager (`systemctl --user daemon-reload`) and enables/starts the `wanderground-embed.service` daemon securely within its virtual environment path.
4. **Pre-Flight Validation Commands**: Conclude the script by executing the Phase 9.1 programmatic test invocations (`opencode mcp call parallel-search web_search ...`) directly to the terminal standard output, printing a final deployment success or failure report matrix.

Generate the scripts now and provide the absolute command execution instructions. I am ready to deploy.

