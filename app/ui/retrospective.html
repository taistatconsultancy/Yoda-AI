<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YodaAI - Retrospective Session</title>
  
  <!-- Favicon -->
  <link rel="icon" href="/ui/favicon.ico" type="image/x-icon">
  <link rel="icon" href="/ui/favicon.png" type="image/png">
  
  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
  <!-- Sortable.js for drag-drop -->
  <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
  
  <style>
    :root {
      --primary-color: #667eea;
      --secondary-color: #764ba2;
      --success-color: #10b981;
      --warning-color: #f59e0b;
      --danger-color: #ef4444;
      --info-color: #3b82f6;
    }
    
    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .retro-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .retro-header {
      background: white;
      border-radius: 15px;
      padding: 20px 30px;
      margin-bottom: 20px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .retro-code {
      font-size: 24px;
      font-weight: bold;
      color: var(--primary-color);
      font-family: 'Courier New', monospace;
    }
    
    .progress-bar-container {
      background: white;
      border-radius: 15px;
      padding: 30px;
      margin-bottom: 20px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .progress-bar-wrapper {
      position: relative;
      margin: 40px 0 20px 0;
    }
    
    .progress-bar-steps {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding-top: 50px;
    }
    
    .progress-bar-line {
      position: absolute;
      top: 50px;
      left: 0;
      right: 0;
      height: 4px;
      background: #e5e7eb;
      z-index: 1;
    }
    
    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
      transition: width 0.5s ease;
      border-radius: 2px;
    }
    
    .progress-step {
      position: relative;
      z-index: 2;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #e5e7eb;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      transition: all 0.3s;
      cursor: default;
    }
    
    .progress-step.active {
      background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
      color: white;
      transform: scale(1.1);
      box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
    }
    
    .progress-step.completed {
      background: var(--success-color);
      color: white;
    }
    
    .progress-step-label {
      margin-top: 8px;
      text-align: center;
      font-size: 12px;
      font-weight: 600;
      color: #6b7280;
      transition: color 0.3s;
      white-space: nowrap;
    }
    
    .progress-step.active .progress-step-label {
      color: var(--primary-color);
      font-weight: 700;
    }
    
    .progress-step.completed .progress-step-label {
      color: var(--success-color);
    }
    
    .text-purple {
      color: #8b5cf6 !important;
    }
    
    .btn-outline-purple {
      border-color: #8b5cf6;
      color: #8b5cf6;
    }
    
    .btn-outline-purple:hover {
      background-color: #8b5cf6;
      color: white;
    }
    
    .border-purple {
      border-color: #8b5cf6 !important;
    }
    
    .main-content {
      background: white;
      border-radius: 15px;
      padding: 30px;
      min-height: 600px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .chat-container {
      height: 500px;
      overflow-y: auto;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
      background: #f9fafb;
    }
    
    .message {
      margin-bottom: 15px;
      padding: 12px;
      border-radius: 10px;
      max-width: 80%;
      animation: fadeIn 0.3s;
      display: flex;
      align-items: flex-start;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .message-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 10px;
      flex-shrink: 0;
      font-size: 20px;
    }
    
    .message.ai .message-avatar {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    .message.user .message-avatar {
      background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
      color: white;
    }
    
    .message-content {
      background: white;
      padding: 12px 15px;
      border-radius: 8px;
      flex: 1;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .message.user {
      flex-direction: row-reverse;
      margin-left: auto;
    }
    
    .message.user .message-avatar {
      margin-left: 10px;
      margin-right: 0;
    }
    
    .message.user .message-content {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    .message.ai {
      background: transparent;
    }
    
    .message.ai .message-content {
      border: 1px solid #e5e7eb;
    }
    
    .message.system {
      background: #fef3c7;
      text-align: center;
      max-width: 100%;
      font-style: italic;
      flex-direction: column;
    }
    
    .fourls-category {
      background: white;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
      border-left: 4px solid;
    }
    
    .fourls-category.liked { border-color: #10b981; }
    .fourls-category.learned { border-color: #3b82f6; }
    .fourls-category.lacked { border-color: #f59e0b; }
    .fourls-category.longed { border-color: #8b5cf6; }
    
    .theme-item {
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 12px 15px;
      margin-bottom: 10px;
      cursor: move;
      transition: all 0.2s;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .theme-item:hover {
      background: #f3f4f6;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .theme-item.dragging {
      opacity: 0.5;
    }
    
    .vote-count {
      display: inline-block;
      background: var(--primary-color);
      color: white;
      border-radius: 20px;
      padding: 4px 12px;
      font-weight: bold;
      margin-left: 10px;
    }
    
    .facilitator-controls {
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 1000;
    }
    
    .btn-next-phase {
      padding: 15px 30px;
      font-size: 18px;
      border-radius: 50px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .participant-list {
      background: #f9fafb;
      border-radius: 10px;
      padding: 15px;
      margin-top: 20px;
    }
    
    .participant {
      display: inline-block;
      background: white;
      border-radius: 20px;
      padding: 5px 15px;
      margin: 5px;
      border: 1px solid #e5e7eb;
    }
    
    .participant.online {
      border-color: var(--success-color);
    }
    
    .participant.facilitator {
      background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
      color: white;
      border: none;
    }
    
    .da-recommendation {
      background: linear-gradient(135deg, #fef3c7, #fde68a);
      border-radius: 10px;
      padding: 20px;
      margin-top: 20px;
      border-left: 4px solid #f59e0b;
    }
    
    .summary-section {
      margin-top: 30px;
    }
    
    .summary-card {
      background: #f9fafb;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 15px;
    }
    
    .loading-spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-20px); }
    }
  </style>
</head>
<body>
  
  <div class="retro-container">
    <!-- Upcoming Retrospectives -->
    <div class="retro-header" id="upcomingRetrosSection" style="display: none;">
      <h5 class="mb-3">Upcoming Retrospectives</h5>
      <div id="upcomingRetros">
        <p class="text-muted">No upcoming retrospectives.</p>
      </div>
    </div>
    <!-- Started Retrospectives -->
    <div class="retro-header" id="startedRetrosSection" style="display: none;">
      <h5 class="mb-3">Started Retrospectives</h5>
      <div id="startedRetros">
        <p class="text-muted">No started retrospectives.</p>
      </div>
    </div>
    
    <!-- Header -->
    <div class="retro-header">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h2 class="mb-1">4Ls Retrospective</h2>
          <p class="text-muted mb-0" id="retroTitle">Loading retrospective...</p>
        </div>
        <div class="text-end">
          <div class="retro-code" id="retroCode">-----</div>
          <small class="text-muted">Session Code</small>
        </div>
      </div>
      
      <div class="participant-list" id="participantList">
        <small class="text-muted">Participants:</small>
        <div id="participants">
          <span class="participant">Loading...</span>
        </div>
      </div>
    </div>
    
    <!-- Progress Bar -->
    <div class="progress-bar-container">
      <div class="progress-bar-wrapper">
        <div class="progress-bar-line">
          <div class="progress-bar-fill" id="progressFill" style="width: 0%"></div>
      </div>
        <div class="progress-bar-steps">
          <div class="progress-step" data-phase="retrospective">
            <i class="bi bi-chat-dots"></i>
            <div class="progress-step-label">Retrospective</div>
      </div>
          <div class="progress-step" data-phase="grouping">
        <i class="bi bi-collection"></i>
            <div class="progress-step-label">Grouping</div>
      </div>
          <div class="progress-step" data-phase="voting">
        <i class="bi bi-hand-thumbs-up"></i>
            <div class="progress-step-label">Voting</div>
      </div>
          <div class="progress-step" data-phase="discussion">
            <i class="bi bi-chat-left-text"></i>
            <div class="progress-step-label">Discussion</div>
      </div>
          <div class="progress-step" data-phase="summary">
        <i class="bi bi-file-text"></i>
            <div class="progress-step-label">Summary</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Content Area -->
    <div class="main-content" id="mainContent">
      <div class="text-center py-5">
        <div class="loading-spinner mb-3"></div>
        <p class="text-muted">Loading retrospective session...</p>
      </div>
    </div>
    
    <!-- Facilitator Controls (shown only to facilitator) -->
    <div class="facilitator-controls" id="facilitatorControls" style="display: none;">
      <button class="btn btn-primary btn-next-phase" onclick="nextPhase()">
        <i class="bi bi-arrow-right-circle"></i> Next Phase
      </button>
    </div>
  </div>
  
  <!-- Bootstrap JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  
  <!-- Main JavaScript -->
  <script>
    // Global variables
    let retroCode = '';
    let retroData = null;
    let currentPhase = 'input';
    let currentUser = null;
    let authToken = null;
    let isFacilitator = false;
    let chatMessages = [];
    let currentChatCategory = null;
    let chatSessionId = null;
    let themes = {
      liked: [],
      learned: [],
      lacked: [],
      longedFor: []
    };
    let pendingVotes = {};
    let votesSubmitted = false;
    let votingPollInterval = null;
    let mainPollInterval = null;
    // Dashboard cache for quick card moves
    window._dashRetrosById = Object.create(null);
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', async function() {
      // Extract retro code from URL
      const pathParts = window.location.pathname.split('/');
      retroCode = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];
      
      // Get auth token from localStorage or URL params
      authToken = localStorage.getItem('yodaai_token') || new URLSearchParams(window.location.search).get('token');
      const userStr = localStorage.getItem('yodaai_user');
      if (userStr) {
        currentUser = JSON.parse(userStr);
      }
      
      if (!authToken) {
        showError('Please log in to join this retrospective.');
        return;
      }
      
      // Load upcoming retrospectives (always)
      await loadUpcomingRetros();
      
      // Load retrospective data if we have a code
      if (retroCode && retroCode !== 'retrospective.html') {
        await loadRetrospective();
      // Start polling for updates (every 3 seconds)
      mainPollInterval = setInterval(pollForUpdates, 3000);
      } else {
        // No specific retrospective - show upcoming list
        document.querySelector('.retro-header:not(#upcomingRetrosSection)').style.display = 'none';
        document.getElementById('facilitatorControls').style.display = 'none';
        document.getElementById('upcomingRetrosSection').style.display = 'block';
        document.getElementById('startedRetrosSection').style.display = 'block';
      }
    });
    
    async function loadRetrospective() {
      try {
        const response = await fetch(`/api/v1/retrospectives/code/${retroCode}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Retrospective not found');
        }
        
        retroData = await response.json();
        
        // Update UI
        document.getElementById('retroCode').textContent = retroCode;
        document.getElementById('retroTitle').textContent = retroData.title || 'Untitled Retrospective';
        
        // Check if current user is facilitator
        isFacilitator = currentUser && retroData.facilitator_id === currentUser.id;
        
        // Set current phase
        currentPhase = retroData.current_phase || 'input';
        
        // Show facilitator controls if applicable and not completed
        if (isFacilitator && currentPhase !== 'completed') {
          document.getElementById('facilitatorControls').style.display = 'block';
        }
        
        updatePhaseIndicator();
        
        // Load participants
        loadParticipants();
        
        // Render current phase
        await renderPhase(currentPhase);
        
      } catch (error) {
        console.error('Load retrospective error:', error);
        showError('Failed to load retrospective: ' + error.message);
      }
    }
    
    function updatePhaseIndicator() {
      const phaseOrder = ['input', 'grouping', 'voting', 'discussion', 'summary'];
      const currentPhaseIndex = phaseOrder.indexOf(currentPhase);
      
      // Map 'input' to 'retrospective' for display
      const displayPhaseMap = {
        'input': 'retrospective',
        'grouping': 'grouping',
        'voting': 'voting',
        'discussion': 'discussion',
        'summary': 'summary',
        'completed': 'summary'
      };
      
      const activePhase = displayPhaseMap[currentPhase] || 'retrospective';
      
      document.querySelectorAll('.progress-step').forEach((step) => {
        const stepPhase = step.dataset.phase;
        step.classList.remove('active', 'completed');
        
        const stepIndex = phaseOrder.indexOf(stepPhase === 'retrospective' ? 'input' : stepPhase);
        
        if (stepPhase === activePhase) {
          step.classList.add('active');
        } else if (stepIndex >= 0 && stepIndex < currentPhaseIndex) {
          step.classList.add('completed');
        }
      });
      
      // Update progress bar fill
      if (currentPhaseIndex >= 0) {
        const progress = ((currentPhaseIndex + 1) / phaseOrder.length) * 100;
        document.getElementById('progressFill').style.width = progress + '%';
      }
    }
    
    async function loadParticipants() {
      try {
        const response = await fetch(`/api/v1/retrospectives/${retroData.id}/participants`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const participants = await response.json();
          displayParticipants(participants);
        }
      } catch (error) {
        console.error('Load participants error:', error);
      }
    }
    
    function displayParticipants(participants) {
      const container = document.getElementById('participants');
      container.innerHTML = '';
      
      participants.forEach(p => {
        const span = document.createElement('span');
        span.className = 'participant';
        if (p.is_online) span.classList.add('online');
        if (p.user_id === retroData.facilitator_id) span.classList.add('facilitator');
        
        const userName = p.user_name || p.full_name || p.email;
        span.innerHTML = `
          ${p.user_id === retroData.facilitator_id ? '<i class="bi bi-star-fill"></i> ' : ''}
          ${escapeHtml(userName)}
        `;
        container.appendChild(span);
      });
    }
    
    async function renderPhase(phase) {
      const content = document.getElementById('mainContent');
      
      // Stop voting polling if leaving voting phase
      if (phase !== 'voting' && votingPollInterval) {
        clearInterval(votingPollInterval);
        votingPollInterval = null;
      }
      
      if (phase === 'input') {
        await renderRetrospectivePhase();
      } else if (phase === 'grouping') {
          renderGroupingPhase();
      } else if (phase === 'voting') {
          renderVotingPhase();
      } else if (phase === 'discussion') {
          renderDiscussionPhase();
      } else if (phase === 'summary') {
          renderSummaryPhase();
      } else if (phase === 'completed') {
        renderCompletedPhase();
      } else {
          content.innerHTML = '<p class="text-center">Invalid phase</p>';
      }
    }
    
    async function renderRetrospectivePhase() {
      const content = document.getElementById('mainContent');
      
      content.innerHTML = `
        <h3 class="mb-4"><i class="bi bi-chat-dots"></i> 4Ls Retrospective</h3>
        <p class="text-muted">Share your thoughts on the sprint through the 4Ls: Liked, Learned, Lacked, and Longed For.</p>
        
        <div class="chat-container" id="chatContainer">
          <div class="text-center text-muted py-5">
            <i class="bi bi-chat-left-dots display-1"></i>
            <p class="mt-3">Loading chat...</p>
          </div>
        </div>
        
        <div class="input-group">
          <input type="text" class="form-control form-control-lg" id="messageInput" 
                 placeholder="Type your message and press Enter..." onkeypress="handleMessageKeyPress(event)">
          <button class="btn btn-primary" onclick="sendMessage()">
            <i class="bi bi-send"></i> Send
          </button>
        </div>
        
        
      `;
      
      // Initialize and load chat session
      await initializeChatSession();
      loadChatSession();
    }
    
    
    async function initializeChatSession() {
      if (chatSessionId) {
        // Session already exists
        return;
      }
      
      try {
        const response = await fetch('/api/v1/fourls-chat/start', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            retrospective_id: retroData.id
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          chatSessionId = data.session_id;
        } else {
          // Try to get existing session
          const linkResponse = await fetch(`/api/v1/fourls-chat/link/by-retro/${retroData.id}`, {
            headers: {
              'Authorization': `Bearer ${authToken}`
            }
          });
          if (linkResponse.ok) {
            const linkData = await linkResponse.json();
            chatSessionId = linkData.session_id;
          }
        }
      } catch (error) {
        console.error('Initialize chat session error:', error);
      }
    }
    
    async function loadChatSession() {
      if (!chatSessionId) {
        await initializeChatSession();
      }
      if (!chatSessionId) return;
      
      try {
        const response = await fetch(`/api/v1/fourls-chat/${chatSessionId}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          displayChatMessagesFromSession(data.messages);
          
          // No finish button; facilitator advances phase
        }
      } catch (error) {
        console.error('Load chat session error:', error);
      }
    }
    
    function displayChatMessagesFromSession(messages) {
      const container = document.getElementById('chatContainer');
      if (!container) return;
      
      container.innerHTML = '';
      
      messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = `message ${msg.message_type === 'assistant' ? 'ai' : (msg.message_type === 'user' ? 'user' : 'system')}`;
        
        const icon = msg.message_type === 'user' ? 
          '<i class="bi bi-person-circle"></i>' : 
          '<i class="bi bi-robot"></i>';
        
        const content = msg.message_type === 'assistant'
          ? `<strong>🤖 YodaAI:</strong><br>${escapeHtml(msg.content)}`
          : `<strong>You:</strong><br>${escapeHtml(msg.content)}`;
        
        div.innerHTML = `
          <div class="message-avatar">${icon}</div>
          <div class="message-content">${content}</div>
        `;
        container.appendChild(div);
      });
      
      container.scrollTop = container.scrollHeight;
    }
    
    async function loadChatMessages(phase) {
      try {
        const response = await fetch(`/api/v1/retrospectives/${retroData.id}/messages?phase=${phase}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          chatMessages = await response.json();
          displayChatMessages();
        }
      } catch (error) {
        console.error('Load messages error:', error);
      }
    }
    
    function displayChatMessages() {
      const container = document.getElementById('chatContainer');
      if (!container) return;
      
      container.innerHTML = '';
      
      chatMessages.forEach(msg => {
        const div = document.createElement('div');
        div.className = `message ${msg.is_ai ? 'ai' : (msg.user_id === currentUser?.id ? 'user' : 'system')}`;
        
        const content = msg.is_ai 
          ? `<strong>🤖 YodaAI:</strong><br>${escapeHtml(msg.content)}`
          : `<strong>${escapeHtml(msg.user_name)}:</strong><br>${escapeHtml(msg.content)}`;
        
        div.innerHTML = content;
        container.appendChild(div);
      });
      
      container.scrollTop = container.scrollHeight;
    }
    
    function handleMessageKeyPress(event) {
      if (event.key === 'Enter') {
        sendMessage();
      }
    }
    
    async function sendMessage() {
      const input = document.getElementById('messageInput');
      const message = input.value.trim();
      
      if (!message) return;
      
      // Show loading state
      const btn = input.nextElementSibling;
      const originalText = btn ? btn.innerHTML : '';
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';
      }
      
      try {
        // Display user message immediately
        const container = document.getElementById('chatContainer');
        const userDiv = document.createElement('div');
        userDiv.className = 'message user';
        userDiv.innerHTML = `
          <div class="message-avatar"><i class="bi bi-person-circle"></i></div>
          <div class="message-content">${escapeHtml(message)}</div>
        `;
        container.appendChild(userDiv);
        container.scrollTop = container.scrollHeight;
        
        // Clear input immediately
        input.value = '';
        
        const response = await fetch(`/api/v1/fourls-chat/${chatSessionId}/message`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: message })
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // Display AI response
          const aiDiv = document.createElement('div');
          aiDiv.className = 'message ai';
          aiDiv.innerHTML = `
            <div class="message-avatar"><i class="bi bi-robot"></i></div>
            <div class="message-content">${escapeHtml(data.message)}</div>
          `;
          container.appendChild(aiDiv);
          container.scrollTop = container.scrollHeight;
          
          // No finish button on completion; facilitator advances phase
        } else {
          const error = await response.json();
          showToast('Failed to send message: ' + (error.detail || 'Unknown error'), 'danger');
        }
      } catch (error) {
        console.error('Send message error:', error);
        showToast('Failed to send message', 'danger');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = originalText;
        }
      }
    }
    
    
    
    function renderGroupingPhase() {
      const content = document.getElementById('mainContent');
      
      if (isFacilitator) {
        content.innerHTML = `
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3 class="mb-0"><i class="bi bi-collection"></i> AI Grouping & Themes</h3>
            </div>
          <p class="text-muted mb-4">AI will analyze all team responses and group them into meaningful themes.</p>
          
          <button id="generateGroupingBtn" onclick="generateGrouping()" class="btn btn-primary btn-lg mb-4">
            <i class="bi bi-magic"></i> Generate AI Grouping
              </button>
          
          <div id="groupingResults">
            <!-- Themes will appear here -->
            </div>
        `;
      } else {
        content.innerHTML = `
          <div class="text-center py-5">
            <i class="bi bi-hourglass-split display-1 text-primary"></i>
            <h3 class="mt-3">Waiting for facilitator to generate grouping...</h3>
        </div>
      `;
      }
      
      if (isFacilitator) {
        loadGroupingResults();
      }
    }
    
    async function generateGrouping() {
      const btn = document.getElementById('generateGroupingBtn');
      const originalText = btn ? btn.innerHTML : '';
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Generating...';
      }
      
      showToast('Generating AI grouping... This may take a moment.', 'info');
      
      try {
        const response = await fetch(`/api/v1/grouping/${retroData.id}/generate`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          showToast(`Created ${data.groups_created || 0} theme groups!`, 'success');
          // Add small delay to ensure database commit is complete
          await new Promise(resolve => setTimeout(resolve, 500));
          await loadGroupingResults();
        } else {
          const error = await response.json();
          showToast('Failed to generate grouping: ' + (error.detail || 'Unknown error'), 'danger');
        }
      } catch (error) {
        console.error('Generate grouping error:', error);
        showToast('Failed to generate grouping. Please try again.', 'danger');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = originalText;
        }
      }
    }
    
    async function loadGroupingResults() {
      try {
        const response = await fetch(`/api/v1/grouping/${retroData.id}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          displayGroupingResults(data);
        } else {
          const error = await response.json();
          console.error('Load grouping error:', error);
          // Show error message in UI
          const container = document.getElementById('groupingResults');
          if (container) {
            container.innerHTML = `<div class="alert alert-warning">Failed to load themes. Please try again.</div>`;
          }
        }
      } catch (error) {
        console.error('Load grouping error:', error);
        const container = document.getElementById('groupingResults');
        if (container) {
          container.innerHTML = `<div class="alert alert-warning">Failed to load themes. Please try again.</div>`;
        }
      }
    }
    
    function displayGroupingResults(data) {
      const container = document.getElementById('groupingResults');
        if (!container) return;
        
      // Group themes by primary_category
      const themesByCategory = {
        'liked': [],
        'learned': [],
        'lacked': [],
        'longed_for': []
      };
      
      data.theme_groups.forEach(theme => {
        const category = theme.primary_category || 'liked';
        if (themesByCategory[category]) {
          themesByCategory[category].push(theme);
        }
      });
      
      let html = '';
      
      // Display themes grouped by 4Ls categories
      const categoryConfig = {
        'liked': { name: 'Liked', icon: 'heart-fill', class: 'liked' },
        'learned': { name: 'Learned', icon: 'lightbulb-fill', class: 'learned' },
        'lacked': { name: 'Lacked', icon: 'exclamation-triangle-fill', class: 'lacked' },
        'longed_for': { name: 'Longed For', icon: 'star-fill', class: 'longed' }
      };
      
      Object.keys(categoryConfig).forEach(category => {
        const config = categoryConfig[category];
        const categoryThemes = themesByCategory[category];
        
        html += `
          <div class="fourls-category ${config.class}">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5><i class="bi bi-${config.icon}"></i> ${config.name}</h5>
              <button class="btn btn-sm btn-success" onclick="addTheme('${category}', ${retroData.id})">
                <i class="bi bi-plus"></i> Add Theme
              </button>
            </div>
            <div id="themes-${category}" class="themes-list">
              ${categoryThemes.map((theme, idx) => `
                <div class="theme-item" data-theme-id="${theme.id}" data-category="${category}">
            <div class="flex-grow-1">
              <strong>${escapeHtml(theme.title)}</strong>
              ${theme.description ? `<br><small class="text-muted">${escapeHtml(theme.description)}</small>` : ''}
            </div>
            <div>
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="editTheme('${category}', ${theme.id}, ${retroData.id})" title="Edit">
                <i class="bi bi-pencil"></i>
              </button>
              <i class="bi bi-grip-vertical text-muted"></i>
                  </div>
                </div>
              `).join('')}
              ${categoryThemes.length === 0 ? '<p class="text-muted text-center py-3">No themes yet</p>' : ''}
            </div>
            </div>
          `;
      });
      
      container.innerHTML = html;
    }
    
    async function saveThemeOrder(category, retroId) {
      const container = document.getElementById(`themes-${category}`);
      if (!container) return;
      
      const themeIds = Array.from(container.children)
        .map(el => el.dataset.themeId)
        .filter(id => id);
      
      try {
        await fetch(`/api/v1/grouping/${retroId}/themes/reorder`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ category, theme_ids: themeIds })
        });
      } catch (error) {
        console.error('Save theme order error:', error);
      }
    }
    
    async function addTheme(category, retroId) {
      const title = prompt('Enter theme title:');
      if (!title) return;
      const description = prompt('Enter theme description (optional):');
      createTheme(category, title, description || '', retroId);
    }
    
    async function createTheme(category, title, description, retroId) {
      try {
        const response = await fetch(`/api/v1/grouping/${retroId}/themes`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ category, title, description })
        });
        if (response.ok) {
          await loadGroupingResults();
          showToast('Theme added successfully', 'success');
        }
      } catch (error) {
        console.error('Create theme error:', error);
        showToast('Failed to add theme', 'danger');
      }
    }
    
    function editTheme(category, themeId, retroId) {
      // Get current theme data from container
      const themeContainer = document.querySelector(`[data-theme-id="${themeId}"]`);
      if (!themeContainer) return;
      
      const titleEl = themeContainer.querySelector('strong');
      const descEl = themeContainer.querySelector('small');
      
      const currentTitle = titleEl ? titleEl.textContent : '';
      const currentDesc = descEl ? descEl.textContent : '';
      
      const newTitle = prompt('Edit theme title:', currentTitle);
      if (!newTitle) return;
      const newDescription = prompt('Edit theme description:', currentDesc);
      updateTheme(themeId, newTitle, newDescription || '', retroId);
    }
    
    async function updateTheme(themeId, title, description, retroId) {
      try {
        const response = await fetch(`/api/v1/grouping/theme/${themeId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ title, description })
        });
        if (response.ok) {
          await loadGroupingResults();
          showToast('Theme updated successfully', 'success');
        }
      } catch (error) {
        console.error('Update theme error:', error);
        showToast('Failed to update theme', 'danger');
      }
      
      // Initialize drag and drop AFTER rendering
      setTimeout(() => {
        ['liked', 'learned', 'lacked', 'longed_for'].forEach(category => {
          const el = document.getElementById(`themes-${category}`);
          if (el) {
            new Sortable(el, {
              animation: 150,
              ghostClass: 'dragging',
              onEnd: function(evt) {
                saveThemeOrder(category, retroData.id);
              }
            });
          }
        });
      }, 100);
    }
    
    function renderVotingPhase() {
      // Initialize voting state
      pendingVotes = {};
      votesSubmitted = false;
      
      const content = document.getElementById('mainContent');
      content.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="mb-0"><i class="bi bi-hand-thumbs-up"></i> Vote on Themes</h3>
        </div>
        <p class="text-muted mb-4">You have 10 votes to allocate to the most important themes. <strong>Your votes won't be saved until you click Submit.</strong></p>
        
        <div id="voteCounter" class="card mb-4">
          <div class="card-body text-center">
            <h4 class="mb-0">Votes: <span id="votesUsed">0</span>/10 allocated</h4>
            <small class="text-muted" id="voteStatus">Draft mode - not submitted</small>
          </div>
        </div>
        
        <div id="votingThemes">
          <!-- Loading themes... -->
        </div>
        
        <div class="mt-4 mb-3">
          <button id="submitVotesBtn" onclick="submitAllVotes()" class="btn btn-primary btn-lg w-100" disabled>
            <i class="bi bi-send"></i> Submit All Votes (<span id="totalPendingVotes">0</span>/10)
          </button>
        </div>
        
        <div id="votingResults" class="mt-4">
          <!-- Results will appear here -->
        </div>
      `;
      
      loadVotingStatus();
      
      // Start voting polling if not already started
      if (!votingPollInterval) {
        votingPollInterval = setInterval(() => {
          loadVotingStatus();
        }, 5000);
      }
    }
    
    async function loadVotingStatus() {
      try {
        const response = await fetch(`/api/v1/voting/${retroData.id}/status`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (!response.ok) {
          // No voting session exists yet - show waiting message
          const themesDiv = document.getElementById('votingThemes');
          if (themesDiv) {
            themesDiv.innerHTML = `
              <div class="alert alert-warning text-center">
                <i class="bi bi-hourglass-split"></i> Waiting for voting session to start...
              </div>
            `;
          }
          return;
        }
        
        const data = await response.json();
        
        // If user already submitted votes, show server data
        if (votesSubmitted) {
          displaySubmittedVotingInterface(data);
          return;
        }
        
        // Display themes with local vote tracking
        const themesDiv = document.getElementById('votingThemes');
        if (!themesDiv) return;
        
        let html = '';
        
        if (data.theme_votes && data.theme_votes.length > 0) {
          data.theme_votes.forEach(theme => {
            const pendingCount = pendingVotes[theme.theme_id] || 0;
            const currentTotal = Object.values(pendingVotes).reduce((sum, v) => sum + v, 0);
            html += `
              <div class="card mb-3">
                <div class="card-body">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:1;">
                      <h5 style="color:#667eea; margin:0 0 5px 0;">
                        <span class="badge bg-info me-2">#${theme.rank || 0}</span>
                        ${escapeHtml(theme.theme_title)}
                      </h5>
                      <p style="color:#666; margin:0;">${escapeHtml(theme.theme_description || '')}</p>
                    </div>
                    <div style="text-align:center; margin-left:20px;">
                      <div style="font-size:20px; font-weight:bold; color:#667eea;">${theme.total_votes || 0}</div>
                      <div style="font-size:12px; color:#888;">total votes</div>
                    </div>
                  </div>
                  <div style="margin-top:15px; display:flex; align-items:center; gap:10px;">
                    <button onclick="adjustLocalVote(${theme.theme_id}, 1)" class="btn btn-sm btn-primary" ${currentTotal >= 10 ? 'disabled' : ''}>
                      <i class="bi bi-plus"></i> +1
                    </button>
                    <button onclick="adjustLocalVote(${theme.theme_id}, -1)" class="btn btn-sm btn-outline-secondary" ${pendingCount === 0 ? 'disabled' : ''}>
                      <i class="bi bi-dash"></i> -1
                    </button>
                    <span style="color:#666; margin-left:10px;">
                      <strong id="pending-${theme.theme_id}">${pendingCount}</strong> pending
                    </span>
                  </div>
                </div>
              </div>
            `;
          });
        } else {
          html = `
            <div class="alert alert-info text-center">
              <i class="bi bi-info-circle"></i> No themes available yet. Please wait for the facilitator to start the voting session.
            </div>
          `;
        }
        
        themesDiv.innerHTML = html;
        
        // Update button state
        updateSubmitButton();
      } catch (error) {
        console.error('Load voting status error:', error);
        const themesDiv = document.getElementById('votingThemes');
        if (themesDiv) {
          themesDiv.innerHTML = `
            <div class="alert alert-danger text-center">
              <i class="bi bi-exclamation-circle"></i> Failed to load voting themes. Please refresh the page.
            </div>
          `;
        }
      }
    }
    
    function displaySubmittedVotingInterface(data) {
      // User has submitted, show read-only view with server data
      const content = document.getElementById('mainContent');
      
      // Show coffee cup wait page if not all participants have voted
      if (!data.all_participants_voted) {
        content.innerHTML = `
          <div class="text-center py-5">
            <div style="font-size: 8rem; animation: float 3s ease-in-out infinite;">
              ☕
            </div>
            <h3 class="mt-4 mb-3" style="color: #667eea;">Grab a Coffee While the Votes Are Being Collected</h3>
            <p class="text-muted mb-4">
              You've submitted your votes! Waiting for other participants to complete their voting.
            </p>
            <div class="alert alert-info d-inline-block">
              <i class="bi bi-people"></i> 
              <strong>${data.participants_who_voted}/${data.total_participants}</strong> participants have voted
            </div>
            <div class="progress mt-3" style="height: 25px; max-width: 400px; margin: 20px auto;">
              <div class="progress-bar progress-bar-striped progress-bar-animated bg-info" 
                   role="progressbar" 
                   style="width: ${(data.participants_who_voted / data.total_participants) * 100}%"
                   aria-valuenow="${data.participants_who_voted}" 
                   aria-valuemin="0" 
                   aria-valuemax="${data.total_participants}">
                ${Math.round((data.participants_who_voted / data.total_participants) * 100)}%
              </div>
            </div>
            <p class="text-muted mt-4">
              <small>This page will automatically refresh when everyone has voted</small>
            </p>
          </div>
        `;
        
        return;
      }
      
      // All participants voted - stop polling and show summary
      if (votingPollInterval) {
        clearInterval(votingPollInterval);
        votingPollInterval = null;
      }
      let html = `
        <div class="d-flex justify-content-between mb-3">
          <h5><i class="bi bi-hand-thumbs-up"></i> Your Votes (Submitted)</h5>
            </div>
        <div class="alert alert-success">
          <i class="bi bi-check-circle"></i> All participants have completed voting!
        </div>
      `;
      
      data.theme_votes.forEach(theme => {
        if (theme.my_votes > 0) {
          html += `
            <div class="card mb-2">
              <div class="card-body">
                <h6 style="color:#667eea; margin:0;">${escapeHtml(theme.theme_title)}</h6>
                <p class="mb-0"><strong>Your votes:</strong> ${theme.my_votes}</p>
              </div>
            </div>
          `;
        }
      });
      
      content.innerHTML = html;
    }
    
    function adjustLocalVote(themeId, delta) {
      const currentTotal = Object.values(pendingVotes).reduce((sum, v) => sum + v, 0);
      
      // Prevent going over 10 votes
      if (delta === 1 && currentTotal >= 10) {
        showToast('You cannot allocate more than 10 votes total', 'warning');
        return;
      }
      
      // Update local pending votes
      pendingVotes[themeId] = (pendingVotes[themeId] || 0) + delta;
      
      if (pendingVotes[themeId] <= 0) {
        delete pendingVotes[themeId];
      }
      
      // Update UI
      const pendingElement = document.getElementById(`pending-${themeId}`);
      if (pendingElement) {
        pendingElement.textContent = pendingVotes[themeId] || 0;
      }
      
      // Update counter and button
      updateVoteCounter();
      updateSubmitButton();
      
      // Re-enable/decrease buttons for all cards
      document.querySelectorAll('.card.mb-3').forEach(card => {
        const increaseBtn = card.querySelector('[onclick*=", 1)"]');
        const decreaseBtn = card.querySelector('[onclick*=", -1)"]');
        const cardThemeId = card.innerHTML.match(/adjustLocalVote\((\d+),/)?.[1];
        
        if (increaseBtn && cardThemeId) {
          const newTotal = Object.values(pendingVotes).reduce((sum, v) => sum + v, 0);
          increaseBtn.disabled = newTotal >= 10;
        }
        
        if (decreaseBtn && cardThemeId) {
          decreaseBtn.disabled = (pendingVotes[cardThemeId] || 0) === 0;
        }
      });
    }
    
    function updateVoteCounter() {
      const total = Object.values(pendingVotes).reduce((sum, v) => sum + v, 0);
      const votesUsedEl = document.getElementById('votesUsed');
      if (votesUsedEl) {
        votesUsedEl.textContent = total;
      }
      const totalPendingEl = document.getElementById('totalPendingVotes');
      if (totalPendingEl) {
        totalPendingEl.textContent = total;
      }
    }
    
    function updateSubmitButton() {
      const total = Object.values(pendingVotes).reduce((sum, v) => sum + v, 0);
      const submitBtn = document.getElementById('submitVotesBtn');
      if (submitBtn) {
        submitBtn.disabled = total === 0 || total > 10;
      }
      
      const statusEl = document.getElementById('voteStatus');
      if (statusEl) {
        if (total === 0) {
          statusEl.textContent = 'No votes allocated yet';
          statusEl.className = 'text-muted';
        } else if (total > 10) {
          statusEl.textContent = `Too many votes! (${total}/10)`;
          statusEl.className = 'text-danger';
        } else {
          statusEl.textContent = `Draft mode - ${total}/10 votes allocated`;
          statusEl.className = 'text-warning';
        }
      }
    }
    
    async function submitAllVotes() {
      const total = Object.values(pendingVotes).reduce((sum, v) => sum + v, 0);
      
      if (total === 0) {
        showToast('Please allocate at least one vote', 'warning');
        return;
      }
      
      if (total > 10) {
        showToast('You cannot allocate more than 10 votes', 'danger');
        return;
      }
      
      // Prepare batch request
      const allocations = Object.entries(pendingVotes).map(([theme_id, votes]) => ({
        theme_group_id: parseInt(theme_id),
        votes: votes
      }));
      
      const btn = document.getElementById('submitVotesBtn');
      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Submitting...';
      
      try {
        const response = await fetch(`/api/v1/voting/${retroData.id}/submit-votes`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ allocations: allocations })
        });
        
        if (response.ok) {
          const data = await response.json();
          showToast(data.message, 'success');
          
          // Mark as submitted
          votesSubmitted = true;
          
          // Reload voting status (will show submitted view)
          loadVotingStatus();
        } else {
          const error = await response.json();
          showToast(error.detail || 'Failed to submit votes', 'danger');
        }
      } catch (error) {
        console.error('Submit votes error:', error);
        showToast('Failed to submit votes', 'danger');
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
    
    function renderDiscussionPhase() {
      const content = document.getElementById('mainContent');
      content.innerHTML = `
        <h3 class="mb-4"><i class="bi bi-chat-dots"></i> Discussion</h3>
        <p class="text-muted">Discuss the top voted themes with the team and get AI insights based on Disciplined Agile.</p>
        
        <div class="row">
          <div class="col-md-6">
            <h5>Top Themes</h5>
            <div id="topThemes"></div>
          </div>
          <div class="col-md-6">
            <h5>AI Discussion Support</h5>
            <div class="chat-container" id="discussionChat" style="height: 400px;"></div>
            <div class="input-group">
              <input type="text" class="form-control" id="discussionInput" 
                     placeholder="Ask AI about the themes..." onkeypress="handleDiscussionKeyPress(event)">
              <button class="btn btn-primary" onclick="sendDiscussionMessage()">
                <i class="bi bi-send"></i>
              </button>
            </div>
          </div>
        </div>
        
        <div class="da-recommendation">
          <h5><i class="bi bi-book"></i> Disciplined Agile Recommendations</h5>
          <div id="daRecommendations">Loading recommendations...</div>
        </div>
      `;
      
      loadTopThemes();
      loadDARecommendations();
    }
    
    async function loadTopThemes() {
      try {
        const response = await fetch(`/api/v1/discussion/${retroData.id}/topics`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const topics = await response.json();
          displayTopThemes(topics);
        }
      } catch (error) {
        console.error('Load top themes error:', error);
      }
    }
    
    function displayTopThemes(topics) {
      const container = document.getElementById('topThemes');
      container.innerHTML = '';
      
      if (!topics || topics.length === 0) {
        container.innerHTML = `
          <div class="alert alert-info">
            <i class="bi bi-info-circle"></i> No discussion topics yet. Topics will be created from voting results.
          </div>
        `;
        return;
      }
      
      topics.forEach((topic) => {
        const div = document.createElement('div');
        div.className = 'theme-item';
        div.innerHTML = `
          <div>
            <strong>#${topic.rank}. ${escapeHtml(topic.theme_title)}</strong>
            <br><small class="text-muted">${escapeHtml(topic.theme_description || '')}</small>
          </div>
          <div class="vote-count">${topic.total_votes} votes</div>
        `;
        container.appendChild(div);
      });
    }
    
    async function loadDARecommendations() {
      try {
        const response = await fetch(`/api/v1/discussion/${retroData.id}/da-recommendations`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const recommendations = await response.json();
          const content = recommendations.content || 'No specific recommendations at this time.';
          
          // Use bullet rendering for better readability
          const formattedContent = renderMarkdownBullets(content);
          document.getElementById('daRecommendations').innerHTML = formattedContent || 'No specific recommendations at this time.';
        }
      } catch (error) {
        console.error('Load DA recommendations error:', error);
      }
    }
    
    function handleDiscussionKeyPress(event) {
      if (event.key === 'Enter') {
        sendDiscussionMessage();
      }
    }
    
    async function sendDiscussionMessage() {
      const input = document.getElementById('discussionInput');
      const message = input.value.trim();
      
      if (!message) return;
      
      // Add user message to chat
      const chatContainer = document.getElementById('discussionChat');
      const userDiv = document.createElement('div');
      userDiv.className = 'message user';
      userDiv.innerHTML = `<strong>You:</strong><br>${escapeHtml(message)}`;
      chatContainer.appendChild(userDiv);
      
      input.value = '';
      chatContainer.scrollTop = chatContainer.scrollHeight;
      
      // Get AI response using general discussion chat
      try {
        const response = await fetch(`/api/v1/discussion/${retroData.id}/chat`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: message })
        });
        
        if (response.ok) {
          const data = await response.json();
          const aiDiv = document.createElement('div');
          aiDiv.className = 'message ai';
          aiDiv.innerHTML = `<strong>🤖 YodaAI:</strong><br>${escapeHtml(data.message)}`;
          chatContainer.appendChild(aiDiv);
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      } catch (error) {
        console.error('Discussion chat error:', error);
      }
    }
    
    function renderSummaryPhase() {
      const content = document.getElementById('mainContent');
      content.innerHTML = `
        <h3 class="mb-4"><i class="bi bi-file-text"></i> Retrospective Summary</h3>
        <p class="text-muted">Review the retrospective outcomes and download the summary.</p>
        
        <div class="text-center mb-4">
          <button class="btn btn-success btn-lg" onclick="generateSummaryPDF()">
            <i class="bi bi-file-pdf"></i> Download PDF Summary
          </button>
        </div>
        
        <div class="summary-section" id="summaryContent">
          <div class="text-center py-4">
            <div class="loading-spinner mb-3"></div>
            <p class="text-muted">Generating summary...</p>
          </div>
        </div>
      `;
      
      loadSummary();
    }
    
    async function loadSummary() {
      try {
        const response = await fetch(`/api/v1/discussion/${retroData.id}/summary`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const summary = await response.json();
          displaySummary(summary);
        } else {
          const container = document.getElementById('summaryContent');
          container.innerHTML = `
            <div class="alert alert-warning">
              <i class="bi bi-exclamation-triangle"></i> Summary is not available yet. Please try again shortly.
            </div>
          `;
        }
      } catch (error) {
        console.error('Load summary error:', error);
        const container = document.getElementById('summaryContent');
        container.innerHTML = `
          <div class="alert alert-danger">
            <i class="bi bi-exclamation-octagon"></i> Failed to load summary. Please refresh and try again.
          </div>
        `;
      }
    }
    
    function displaySummary(summary) {
      const container = document.getElementById('summaryContent');
      container.innerHTML = `
        <div class="summary-card">
          <h5><i class="bi bi-file-text"></i> Sprint Summary</h5>
          <p style="white-space: pre-wrap;">${escapeHtml(summary.summary || 'No summary generated yet.')}</p>
        </div>
        
        ${summary.achievements && summary.achievements.length > 0 ? `
        <div class="summary-card">
          <h5><i class="bi bi-trophy"></i> Achievements</h5>
          <ul>
            ${summary.achievements.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
          </ul>
        </div>
        ` : ''}
        
        ${summary.challenges && summary.challenges.length > 0 ? `
        <div class="summary-card">
          <h5><i class="bi bi-exclamation-triangle"></i> Challenges</h5>
          <ul>
            ${summary.challenges.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
          </ul>
        </div>
        ` : ''}
        
        ${summary.recommendations && summary.recommendations.length > 0 ? `
        <div class="summary-card">
          <h5><i class="bi bi-lightbulb"></i> Recommendations</h5>
          <ul>
            ${summary.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
          </ul>
        </div>
        ` : ''}
        
        ${summary.da_recommendations ? `
        <div class="summary-card">
          <h5><i class="bi bi-book"></i> Disciplined Agile Recommendations</h5>
          ${renderMarkdownBullets(summary.da_recommendations)}
        </div>
        ` : ''}
        
        ${summary.voting_results && summary.voting_results.length > 0 ? `
        <div class="summary-card">
          <h5><i class="bi bi-bar-chart"></i> Voting Results</h5>
          <div class="table-responsive">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Theme</th>
                  <th class="text-center">Votes</th>
                </tr>
              </thead>
              <tbody>
                ${summary.voting_results.map((result, idx) => `
                  <tr>
                    <td class="text-muted">${idx + 1}</td>
                    <td>
                      <strong>${escapeHtml(result.theme_title)}</strong><br>
                      <small class="text-muted">${escapeHtml(result.theme_description || '')}</small>
                    </td>
                    <td class="text-center">
                      <span class="badge bg-primary">${result.total_votes}</span>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
        ` : ''}
      `;
      
      // Load previous retros
      loadPreviousRetros();
    }

    // Render markdown-like content as bullet points with bold support
    function renderMarkdownBullets(raw) {
      if (!raw) return '<p class="text-muted">No recommendations.</p>';
      // Preserve bold markers by converting to HTML then escaping
      let marked = raw.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      let escaped = escapeHtml(marked)
        .replace(/&lt;strong&gt;/g, '<strong>')
        .replace(/&lt;\/strong&gt;/g, '</strong>');
      // Split into lines and create bullets for lines starting with '-' or '•'
      const lines = escaped.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
      if (lines.length === 0) return '<p class="text-muted">No recommendations.</p>';
      const items = [];
      lines.forEach(line => {
        const bulletMatch = line.match(/^[-•]\s*(.*)$/);
        if (bulletMatch) {
          items.push(`<li>${bulletMatch[1]}</li>`);
        } else {
          // Treat sentences separated by ' - ' as bullet segments
          const parts = line.split(/\s-\s/);
          if (parts.length > 1) {
            parts.forEach(p => items.push(`<li>${p}</li>`));
          } else {
            items.push(`<li>${line}</li>`);
          }
        }
      });
      return `<ul>${items.join('')}</ul>`;
    }
    
    async function loadPreviousRetros() {
      try {
        const response = await fetch(`/api/v1/workspaces/${retroData.workspace_id}/retrospectives/history`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const history = await response.json();
          displayPreviousRetros(history);
        }
      } catch (error) {
        console.error('Load previous retros error:', error);
      }
    }
    
    function displayPreviousRetros(history) {
      const container = document.getElementById('previousRetros');
      if (!history || history.length === 0) {
        container.innerHTML = '<p class="text-muted">No previous retrospectives.</p>';
        return;
      }
      
      // Use the most recent row by id (DB-insertion order) as the last retrospective
      let last = history.reduce((acc, cur) => (acc == null || (cur.id && cur.id > (acc.id || 0)) ? cur : acc), null);
      if (!last) {
        container.innerHTML = '<p class="text-muted">No previous retrospectives.</p>';
        return;
      }
      const when = last.actual_start_time ? new Date(last.actual_start_time) : new Date(last.created_at);
      
      container.innerHTML = '';
      const div = document.createElement('div');
      div.className = 'mb-2';
      div.innerHTML = `
        <a href="/ui/retrospective.html/${last.code}" target="_blank">
          ${escapeHtml(last.title)} - ${when.toLocaleDateString()} ${when.toLocaleTimeString()}
        </a>
      `;
      container.appendChild(div);
    }
    
    async function generateSummaryPDF() {
      try {
        showToast('Generating PDF...', 'info');
        
        const response = await fetch(`/api/v1/discussion/${retroData.id}/summary/pdf`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `retrospective-${retroCode}.pdf`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
          showToast('PDF downloaded successfully!', 'success');
        } else {
          throw new Error('Failed to generate PDF');
        }
      } catch (error) {
        console.error('Generate PDF error:', error);
        showToast('Failed to generate PDF', 'danger');
      }
    }
    
    function renderCompletedPhase() {
      const content = document.getElementById('mainContent');
      
      // Stop all polling on completion
      if (votingPollInterval) {
        clearInterval(votingPollInterval);
        votingPollInterval = null;
      }
      if (mainPollInterval) {
        clearInterval(mainPollInterval);
        mainPollInterval = null;
      }
      
      // Hide facilitator controls
      const facilitatorControls = document.getElementById('facilitatorControls');
      if (facilitatorControls) {
        facilitatorControls.style.display = 'none';
      }
      
      content.innerHTML = `
        <div class="text-center py-5">
          <div class="mb-4">
            <i class="bi bi-check-circle-fill text-success display-1"></i>
          </div>
          <h2 class="mb-3">Retrospective Complete!</h2>
          <p class="text-muted mb-4">Thank you for participating in this retrospective. All participants are being redirected to their dashboard.</p>
          <div class="alert alert-info" role="alert">
            <i class="bi bi-info-circle"></i> Redirecting to dashboard in <span id="redirectCountdown">5</span> seconds...
          </div>
          <button class="btn btn-primary btn-lg" onclick="goToDashboard()">
            <i class="bi bi-speedometer2"></i> Go to Dashboard Now
          </button>
        </div>
      `;
      
      // Start countdown
      let countdown = 5;
      const countdownEl = document.getElementById('redirectCountdown');
      const countdownInterval = setInterval(() => {
        countdown--;
        if (countdownEl) countdownEl.textContent = countdown;
        if (countdown <= 0) {
          clearInterval(countdownInterval);
          goToDashboard();
        }
      }, 1000);
    }
    
    function goToDashboard() {
      window.location.href = '/ui/yodaai-app.html';
    }
    
    async function nextPhase() {
      if (!isFacilitator) {
        showToast('Only the facilitator can advance phases', 'warning');
        return;
      }
      
      if (currentPhase === 'completed') {
        showToast('Retrospective is already complete!', 'info');
        return;
      }
      
      // Disable the Next Phase button to prevent double-pressing
      const btn = document.querySelector('.btn-next-phase');
      const originalText = btn ? btn.innerHTML : '';
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
      }
      
      try {
        // Determine next phase
        const phaseOrder = ['input', 'grouping', 'voting', 'discussion', 'summary', 'completed'];
        const currentIndex = phaseOrder.indexOf(currentPhase);
        const nextPhase = phaseOrder[currentIndex + 1];
        
        if (!nextPhase) {
          showToast('No more phases available', 'warning');
          return;
        }
        
        // If moving to voting, start voting session first
        if (nextPhase === 'voting') {
          try {
            await fetch(`/api/v1/voting/${retroData.id}/start`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authToken}`
              }
            });
          } catch (error) {
            console.error('Start voting session error:', error);
          }
        }
        
        // If moving from input phase, complete all chat sessions
        if (currentPhase === 'input' && nextPhase === 'grouping') {
          try {
            await fetch(`/api/v1/retrospectives/${retroData.id}/complete-chat-sessions`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authToken}`
              }
            });
          } catch (error) {
            console.error('Complete chat sessions error:', error);
          }
        }
        
        // If moving from voting to discussion, finalize voting first to create topics
        if (currentPhase === 'voting' && nextPhase === 'discussion') {
          try {
            await fetch(`/api/v1/voting/${retroData.id}/finalize`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authToken}`
              }
            });
          } catch (error) {
            console.error('Finalize voting error:', error);
          }
        }
        
        // Stop all polling before advancing phase
        if (votingPollInterval) {
          clearInterval(votingPollInterval);
          votingPollInterval = null;
        }
        if (mainPollInterval) {
          clearInterval(mainPollInterval);
          mainPollInterval = null;
        }
        
        // Advance phase
        const response = await fetch(`/api/v1/retrospectives/${retroData.id}/advance-phase`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          currentPhase = data.current_phase;
          updatePhaseIndicator();
          renderPhase(currentPhase);
          showToast(`Moved to phase ${currentPhase}`, 'success');
          
          // Don't restart polling or re-enable button if we're in completed phase
          if (currentPhase !== 'completed') {
            // Restart main polling after phase change
            if (!mainPollInterval) {
              mainPollInterval = setInterval(pollForUpdates, 3000);
            }
            
            // Re-enable button
            if (btn) {
              btn.disabled = false;
              btn.innerHTML = originalText;
            }
          } else {
            // Hide facilitator controls on completion
            const facilitatorControls = document.getElementById('facilitatorControls');
            if (facilitatorControls) {
              facilitatorControls.style.display = 'none';
            }
          }
        } else {
          // Re-enable button on error
          if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
          }
        }
      } catch (error) {
        console.error('Next phase error:', error);
        showToast('Failed to advance phase', 'danger');
        // Re-enable button on error
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = originalText;
        }
      }
    }
    
    async function pollForUpdates() {
      if (!retroData) return;
      
      try {
        const response = await fetch(`/api/v1/retrospectives/${retroData.id}/status`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (response.ok) {
          const status = await response.json();
          
          // Check if phase changed
          if (status.current_phase !== currentPhase) {
            currentPhase = status.current_phase;
            updatePhaseIndicator();
            renderPhase(currentPhase);
            showToast('Phase updated by facilitator', 'info');
          }
          
          // Update participants
          if (status.participants) {
            displayParticipants(status.participants);
          }
        }
      } catch (error) {
        // Silently fail polling errors
      }
    }
    
    function showError(message) {
      document.getElementById('mainContent').innerHTML = `
        <div class="alert alert-danger text-center">
          <i class="bi bi-exclamation-triangle display-1"></i>
          <h4 class="mt-3">${message}</h4>
          <a href="/" class="btn btn-primary mt-3">Return to Home</a>
        </div>
      `;
    }
    
    function showToast(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `alert alert-${type} position-fixed bottom-0 start-50 translate-middle-x mb-3`;
      toast.style.zIndex = '9999';
      toast.style.minWidth = '300px';
      toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
        ${message}
      `;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }
    
    function escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
    
  async function loadUpcomingRetros() {
      const container = document.getElementById('upcomingRetros');
    const startedContainer = document.getElementById('startedRetros');
      if (!container) return;
      
      try {
        const response = await fetch('/api/v1/retrospectives/user/dashboard', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          console.error('Failed to load upcoming retros');
          return;
        }
        
    const dashboard = await response.json();
    const upcoming = dashboard.upcoming || [];
    const started = dashboard.in_progress || [];
        
    if (upcoming.length === 0) {
          container.innerHTML = '<p class="text-muted">No upcoming retrospectives. Create one to get started!</p>';
    } else {
      container.innerHTML = upcoming.map(retro => {
        window._dashRetrosById[retro.id] = retro;
        const cardId = `retro-card-${retro.id}`;
        return `
          <div class="card mb-2 border-start border-4 border-info" id="${cardId}">
            <div class="card-body py-3">
              <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                  <h6 class="mb-1">
                    <i class="bi bi-calendar-event"></i> ${escapeHtml(retro.title)}
                  </h6>
                  ${retro.sprint_name ? `<small class=\"text-muted d-block mb-2\">${escapeHtml(retro.sprint_name)}</small>` : ''}
                  <div class="d-flex gap-3 flex-wrap">
                    <div id="timer-${retro.id}">
                      <small class="text-muted">
                        <i class="bi bi-clock"></i> Loading...
                      </small>
                    </div>
                  </div>
                </div>
                <div id="action-${retro.id}">
                  <button class="btn btn-sm btn-secondary" disabled>
                    <i class="bi bi-lock"></i> Waiting
                  </button>
                </div>
              </div>
            </div>
          </div>
        `;
      }).join('');
      // Start countdown timers for each retrospective
      upcoming.forEach(retro => {
        const startDate = retro.scheduled_start_time ? new Date(retro.scheduled_start_time) : null;
        if (startDate) {
          startCountdown(retro.id, retro.code, startDate);
        }
      });
        }

    if (startedContainer) {
      if (!started || started.length === 0) {
        startedContainer.innerHTML = '<p class="text-muted">No started retrospectives.</p>';
      } else {
        startedContainer.innerHTML = started.map(retro => {
          window._dashRetrosById[retro.id] = retro;
          return `
            <div class="card mb-2 border-start border-4 border-success" id="started-card-${retro.id}">
              <div class="card-body py-3 d-flex justify-content-between align-items-center">
                <div class="flex-grow-1">
                  <h6 class="mb-1">
                    <i class="bi bi-check-circle"></i> ${escapeHtml(retro.title)}
                  </h6>
                  ${retro.sprint_name ? `<small class=\"text-muted d-block\">${escapeHtml(retro.sprint_name)}</small>` : ''}
                </div>
                <div>
                  <button class="btn btn-sm btn-primary" onclick="joinRetrospective('${retro.code}')">
                    <i class="bi bi-play-circle"></i> Join Now
                  </button>
                </div>
              </div>
            </div>
          `;
        }).join('');
      }
    }
      } catch (error) {
        console.error('Load upcoming retros error:', error);
      }
    }
    
    function startCountdown(retroId, retroCode, startDate) {
      const timerEl = document.getElementById(`timer-${retroId}`);
      const actionEl = document.getElementById(`action-${retroId}`);
    const cardEl = document.getElementById(`retro-card-${retroId}`);
    const startedSection = document.getElementById('startedRetros');
      
      if (!timerEl || !actionEl) return;
      
      function updateCountdown() {
        const now = new Date();
        const diffMs = startDate - now;
        
        if (diffMs <= 0) {
          // Time has elapsed - show join button
          timerEl.innerHTML = `
            <small class="text-success">
              <i class="bi bi-check-circle"></i> Started
            </small>
          `;
          actionEl.innerHTML = `
            <button class="btn btn-sm btn-primary" onclick="joinRetrospective('${retroCode}')">
              <i class="bi bi-play-circle"></i> Join Now
            </button>
          `;
        // Move card from upcoming to started section so it remains visible
        try {
          if (startedSection && cardEl) {
            const retro = window._dashRetrosById[retroId];
            const startedHtml = `
              <div class=\"card mb-2 border-start border-4 border-success\" id=\"started-card-${retroId}\">\n\
                <div class=\"card-body py-3 d-flex justify-content-between align-items-center\">\n\
                  <div class=\"flex-grow-1\">\n\
                    <h6 class=\"mb-1\">\n\
                      <i class=\"bi bi-check-circle\"></i> ${escapeHtml(retro?.title || '')}\n\
                    </h6>\n\
                    ${retro?.sprint_name ? `<small class=\\\"text-muted d-block\\\">${escapeHtml(retro.sprint_name)}</small>` : ''}\n\
                  </div>\n\
                  <div>\n\
                    <button class=\"btn btn-sm btn-primary\" onclick=\"joinRetrospective('${retroCode}')\">\n\
                      <i class=\"bi bi-play-circle\"></i> Join Now\n\
                    </button>\n\
                  </div>\n\
                </div>\n\
              </div>`;
            if (startedSection.querySelector('.text-muted')) startedSection.innerHTML = '';
            startedSection.insertAdjacentHTML('afterbegin', startedHtml);
            // Remove from upcoming
            const parent = cardEl.parentNode; if (parent) parent.removeChild(cardEl);
          }
          // Ensure the section is visible
          document.getElementById('startedRetrosSection').style.display = 'block';
        } catch(e) { /* ignore */ }
          return;
        }
        
        const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        let timeStr = '';
        if (days > 0) {
          timeStr = `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
          timeStr = `${hours}h ${minutes}m ${seconds}s`;
        } else {
          timeStr = `${minutes}m ${seconds}s`;
        }
        
        timerEl.innerHTML = `
          <small class="text-info">
            <i class="bi bi-clock"></i> In ${timeStr}
          </small>
        `;
        
        // Schedule next update
        setTimeout(updateCountdown, 1000);
      }
      
      // Initial update
      updateCountdown();
    }
    
    async function joinRetrospective(code) {
      // Simply navigate to the retrospective page with the code
      window.location.href = `/ui/retrospective.html/${code}`;
    }
  </script>
</body>
</html>

