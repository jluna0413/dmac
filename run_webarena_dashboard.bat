@echo off
echo Activating DMac virtual environment...
call .\dmac_env\Scripts\activate

echo Running WebArena Dashboard...
cd OpenManus-RL\openmanus_rl\agentgym\agentenv-webarena\webarena\scripts
streamlit run webarena_dashboard.py

echo Press any key to exit...
pause > nul
