-- ============================================================================
-- YodaAI Complete Database Schema
-- Comprehensive schema for retrospective management system
-- ============================================================================

-- Drop existing tables (in reverse order of dependencies)
DROP TABLE IF EXISTS action_item_comments CASCADE;
DROP TABLE IF EXISTS action_items CASCADE;
DROP TABLE IF EXISTS discussion_messages CASCADE;
DROP TABLE IF EXISTS discussion_topics CASCADE;
DROP TABLE IF EXISTS vote_allocations CASCADE;
DROP TABLE IF EXISTS voting_sessions CASCADE;
DROP TABLE IF EXISTS grouped_themes CASCADE;
DROP TABLE IF EXISTS theme_groups CASCADE;
DROP TABLE IF EXISTS retrospective_responses CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS retrospective_participants CASCADE;
DROP TABLE IF EXISTS retrospectives CASCADE;
DROP TABLE IF EXISTS workspace_invitations CASCADE;
DROP TABLE IF EXISTS workspace_members CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;
DROP TABLE IF EXISTS email_verification_tokens CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop existing types
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS workspace_role CASCADE;
DROP TYPE IF EXISTS retrospective_status CASCADE;
DROP TYPE IF EXISTS retrospective_phase CASCADE;
DROP TYPE IF EXISTS response_category CASCADE;
DROP TYPE IF EXISTS invitation_status CASCADE;
DROP TYPE IF EXISTS action_item_status CASCADE;
DROP TYPE IF EXISTS action_item_priority CASCADE;

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE user_role AS ENUM ('facilitator', 'member', 'admin');
CREATE TYPE workspace_role AS ENUM ('owner', 'facilitator', 'member', 'viewer');
CREATE TYPE retrospective_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE retrospective_phase AS ENUM ('input', 'grouping', 'voting', 'discussion', 'summary', 'completed');
CREATE TYPE response_category AS ENUM ('liked', 'learned', 'lacked', 'longed_for');
CREATE TYPE invitation_status AS ENUM ('pending', 'accepted', 'declined', 'expired');
CREATE TYPE action_item_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled', 'blocked');
CREATE TYPE action_item_priority AS ENUM ('low', 'medium', 'high', 'critical');

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255),
    
    -- Email verification
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- OAuth
    google_id VARCHAR(255) UNIQUE,
    profile_picture_url TEXT,
    
    -- User preferences
    default_role user_role DEFAULT 'member',
    timezone VARCHAR(50) DEFAULT 'UTC',
    notification_preferences JSONB DEFAULT '{"email": true, "in_app": true}'::jsonb,
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email_verified ON users(email_verified);

-- ============================================================================
-- EMAIL VERIFICATION TOKENS
-- ============================================================================

CREATE TABLE email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_verification_tokens_user ON email_verification_tokens(user_id);
CREATE INDEX idx_verification_tokens_token ON email_verification_tokens(token);

-- ============================================================================
-- WORKSPACES TABLE
-- ============================================================================

CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Owner
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Settings
    settings JSONB DEFAULT '{
        "allow_anonymous_responses": false,
        "require_email_verification": true,
        "auto_archive_after_days": 90,
        "max_members": 100
    }'::jsonb,
    
    -- Workspace status
    is_active BOOLEAN DEFAULT TRUE,
    archived_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workspaces_created_by ON workspaces(created_by);
CREATE INDEX idx_workspaces_active ON workspaces(is_active);

-- ============================================================================
-- WORKSPACE MEMBERS
-- ============================================================================

CREATE TABLE workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role workspace_role NOT NULL DEFAULT 'member',
    
    -- Member status
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_active ON workspace_members(workspace_id, is_active);

-- ============================================================================
-- WORKSPACE INVITATIONS
-- ============================================================================

CREATE TABLE workspace_invitations (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    invited_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Invitee info
    email VARCHAR(255) NOT NULL,
    role workspace_role DEFAULT 'member',
    
    -- Invitation details
    token VARCHAR(255) NOT NULL UNIQUE,
    status invitation_status DEFAULT 'pending',
    message TEXT,
    
    -- Timestamps
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    declined_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_invitations_workspace ON workspace_invitations(workspace_id);
CREATE INDEX idx_invitations_email ON workspace_invitations(email);
CREATE INDEX idx_invitations_token ON workspace_invitations(token);
CREATE INDEX idx_invitations_status ON workspace_invitations(status);

-- ============================================================================
-- RETROSPECTIVES TABLE
-- ============================================================================

CREATE TABLE retrospectives (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    
    -- Basic info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sprint_name VARCHAR(100),
    
    -- Facilitation
    facilitator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Scheduling
    scheduled_start_time TIMESTAMP WITH TIME ZONE,
    scheduled_end_time TIMESTAMP WITH TIME ZONE,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    
    -- Status and phase
    status retrospective_status DEFAULT 'scheduled',
    current_phase retrospective_phase DEFAULT 'input',
    
    -- Phase completion tracking
    phase_completion JSONB DEFAULT '{
        "input": false,
        "grouping": false,
        "voting": false,
        "discussion": false,
        "summary": false
    }'::jsonb,
    
    -- Settings
    settings JSONB DEFAULT '{
        "votes_per_member": 10,
        "min_votes_for_discussion": 3,
        "discussion_time_per_topic": 15,
        "allow_anonymous": false
    }'::jsonb,
    
    -- AI-generated content
    ai_summary TEXT,
    ai_insights JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_retrospectives_workspace ON retrospectives(workspace_id);
CREATE INDEX idx_retrospectives_facilitator ON retrospectives(facilitator_id);
CREATE INDEX idx_retrospectives_status ON retrospectives(status);
CREATE INDEX idx_retrospectives_phase ON retrospectives(current_phase);
CREATE INDEX idx_retrospectives_scheduled ON retrospectives(scheduled_start_time);

-- ============================================================================
-- RETROSPECTIVE PARTICIPANTS
-- ============================================================================

CREATE TABLE retrospective_participants (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Participation tracking
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    joined_at TIMESTAMP WITH TIME ZONE,
    completed_input BOOLEAN DEFAULT FALSE,
    completed_voting BOOLEAN DEFAULT FALSE,
    
    -- Notification tracking
    email_notification_sent BOOLEAN DEFAULT FALSE,
    reminder_sent BOOLEAN DEFAULT FALSE,
    
    UNIQUE(retrospective_id, user_id)
);

CREATE INDEX idx_retro_participants_retro ON retrospective_participants(retrospective_id);
CREATE INDEX idx_retro_participants_user ON retrospective_participants(user_id);

-- ============================================================================
-- CHAT SESSIONS (for 4Ls input phase)
-- ============================================================================

CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session info
    session_id VARCHAR(255) NOT NULL UNIQUE,
    session_type VARCHAR(50) DEFAULT '4ls_input',
    
    -- Progress tracking
    current_category response_category DEFAULT 'liked',
    categories_completed JSONB DEFAULT '{
        "liked": false,
        "learned": false,
        "lacked": false,
        "longed_for": false
    }'::jsonb,
    
    -- Session status
    is_active BOOLEAN DEFAULT TRUE,
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_retro ON chat_sessions(retrospective_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);

-- ============================================================================
-- CHAT MESSAGES
-- ============================================================================

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    
    -- Message content
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    
    -- AI metadata
    ai_model VARCHAR(50),
    ai_tokens_used INTEGER,
    
    -- Context
    current_category response_category,
    metadata JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_type ON chat_messages(message_type);

-- ============================================================================
-- RETROSPECTIVE RESPONSES (Extracted from chat)
-- ============================================================================

CREATE TABLE retrospective_responses (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_session_id INTEGER REFERENCES chat_sessions(id) ON DELETE SET NULL,
    
    -- Response content
    category response_category NOT NULL,
    content TEXT NOT NULL,
    
    -- AI analysis
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    keywords JSONB,
    
    -- Grouping (will be populated during grouping phase)
    theme_group_id INTEGER, -- Foreign key added later
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_responses_retro ON retrospective_responses(retrospective_id);
CREATE INDEX idx_responses_user ON retrospective_responses(user_id);
CREATE INDEX idx_responses_category ON retrospective_responses(category);

-- ============================================================================
-- THEME GROUPS (AI-generated groupings)
-- ============================================================================

CREATE TABLE theme_groups (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    
    -- Group info
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- AI-generated
    ai_generated BOOLEAN DEFAULT TRUE,
    ai_confidence DECIMAL(3,2), -- 0.0 to 1.0
    
    -- Categorization
    primary_category response_category,
    
    -- Position for display ordering
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_theme_groups_retro ON theme_groups(retrospective_id);

-- Add foreign key to retrospective_responses
ALTER TABLE retrospective_responses 
ADD CONSTRAINT fk_responses_theme_group 
FOREIGN KEY (theme_group_id) REFERENCES theme_groups(id) ON DELETE SET NULL;

CREATE INDEX idx_responses_theme_group ON retrospective_responses(theme_group_id);

-- ============================================================================
-- GROUPED THEMES (Many-to-many relationship)
-- ============================================================================

CREATE TABLE grouped_themes (
    id SERIAL PRIMARY KEY,
    theme_group_id INTEGER NOT NULL REFERENCES theme_groups(id) ON DELETE CASCADE,
    response_id INTEGER NOT NULL REFERENCES retrospective_responses(id) ON DELETE CASCADE,
    
    -- Grouping metadata
    confidence_score DECIMAL(3,2),
    manually_assigned BOOLEAN DEFAULT FALSE,
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(theme_group_id, response_id)
);

CREATE INDEX idx_grouped_themes_group ON grouped_themes(theme_group_id);
CREATE INDEX idx_grouped_themes_response ON grouped_themes(response_id);

-- ============================================================================
-- VOTING SESSIONS
-- ============================================================================

CREATE TABLE voting_sessions (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    
    -- Voting configuration
    votes_per_member INTEGER DEFAULT 10,
    min_votes_to_discuss INTEGER DEFAULT 3,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_voting_sessions_retro ON voting_sessions(retrospective_id);

-- ============================================================================
-- VOTE ALLOCATIONS
-- ============================================================================

CREATE TABLE vote_allocations (
    id SERIAL PRIMARY KEY,
    voting_session_id INTEGER NOT NULL REFERENCES voting_sessions(id) ON DELETE CASCADE,
    theme_group_id INTEGER NOT NULL REFERENCES theme_groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Vote details
    votes_allocated INTEGER NOT NULL DEFAULT 1 CHECK (votes_allocated >= 0),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(voting_session_id, theme_group_id, user_id)
);

CREATE INDEX idx_vote_allocations_session ON vote_allocations(voting_session_id);
CREATE INDEX idx_vote_allocations_theme ON vote_allocations(theme_group_id);
CREATE INDEX idx_vote_allocations_user ON vote_allocations(user_id);

-- ============================================================================
-- DISCUSSION TOPICS (Top voted themes)
-- ============================================================================

CREATE TABLE discussion_topics (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    theme_group_id INTEGER NOT NULL REFERENCES theme_groups(id) ON DELETE CASCADE,
    
    -- Topic metadata
    total_votes INTEGER DEFAULT 0,
    rank INTEGER,
    
    -- Discussion tracking
    time_allocated_minutes INTEGER DEFAULT 15,
    discussion_started_at TIMESTAMP WITH TIME ZONE,
    discussion_ended_at TIMESTAMP WITH TIME ZONE,
    is_discussed BOOLEAN DEFAULT FALSE,
    
    -- AI facilitation
    ai_summary TEXT,
    key_points JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_discussion_topics_retro ON discussion_topics(retrospective_id);
CREATE INDEX idx_discussion_topics_theme ON discussion_topics(theme_group_id);
CREATE INDEX idx_discussion_topics_rank ON discussion_topics(rank);

-- ============================================================================
-- DISCUSSION MESSAGES (AI-facilitated discussion)
-- ============================================================================

CREATE TABLE discussion_messages (
    id SERIAL PRIMARY KEY,
    discussion_topic_id INTEGER NOT NULL REFERENCES discussion_topics(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Message content
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL, -- 'user', 'ai_facilitator', 'system'
    
    -- AI metadata
    ai_model VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_discussion_messages_topic ON discussion_messages(discussion_topic_id);
CREATE INDEX idx_discussion_messages_user ON discussion_messages(user_id);

-- ============================================================================
-- ACTION ITEMS
-- ============================================================================

CREATE TABLE action_items (
    id SERIAL PRIMARY KEY,
    retrospective_id INTEGER NOT NULL REFERENCES retrospectives(id) ON DELETE CASCADE,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    discussion_topic_id INTEGER REFERENCES discussion_topics(id) ON DELETE SET NULL,
    
    -- Action item details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Assignment
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Priority and status
    priority action_item_priority DEFAULT 'medium',
    status action_item_status DEFAULT 'pending',
    
    -- Dates
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- AI-generated
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_confidence DECIMAL(3,2),
    
    -- Tracking
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_action_items_retro ON action_items(retrospective_id);
CREATE INDEX idx_action_items_workspace ON action_items(workspace_id);
CREATE INDEX idx_action_items_assigned_to ON action_items(assigned_to);
CREATE INDEX idx_action_items_status ON action_items(status);
CREATE INDEX idx_action_items_priority ON action_items(priority);
CREATE INDEX idx_action_items_due_date ON action_items(due_date);

-- ============================================================================
-- ACTION ITEM COMMENTS
-- ============================================================================

CREATE TABLE action_item_comments (
    id SERIAL PRIMARY KEY,
    action_item_id INTEGER NOT NULL REFERENCES action_items(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Comment content
    content TEXT NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_action_comments_item ON action_item_comments(action_item_id);
CREATE INDEX idx_action_comments_user ON action_item_comments(user_id);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for workspace member details
CREATE VIEW workspace_members_detailed AS
SELECT 
    wm.id,
    wm.workspace_id,
    wm.user_id,
    wm.role,
    wm.is_active,
    wm.joined_at,
    u.email,
    u.full_name,
    u.profile_picture_url
FROM workspace_members wm
JOIN users u ON wm.user_id = u.id;

-- View for retrospective summary
CREATE VIEW retrospective_summary AS
SELECT 
    r.id,
    r.workspace_id,
    r.title,
    r.sprint_name,
    r.status,
    r.current_phase,
    r.scheduled_start_time,
    r.facilitator_id,
    u.full_name as facilitator_name,
    (SELECT COUNT(*) FROM retrospective_participants WHERE retrospective_id = r.id) as participant_count,
    (SELECT COUNT(*) FROM retrospective_responses WHERE retrospective_id = r.id) as response_count,
    (SELECT COUNT(*) FROM action_items WHERE retrospective_id = r.id) as action_item_count,
    r.created_at
FROM retrospectives r
JOIN users u ON r.facilitator_id = u.id;

-- View for theme group with vote counts
CREATE VIEW theme_groups_with_votes AS
SELECT 
    tg.id,
    tg.retrospective_id,
    tg.title,
    tg.description,
    tg.primary_category,
    (SELECT COUNT(*) FROM grouped_themes WHERE theme_group_id = tg.id) as response_count,
    (SELECT COALESCE(SUM(va.votes_allocated), 0) 
     FROM vote_allocations va 
     JOIN voting_sessions vs ON va.voting_session_id = vs.id 
     WHERE va.theme_group_id = tg.id AND vs.retrospective_id = tg.retrospective_id) as total_votes
FROM theme_groups tg;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_retrospectives_updated_at BEFORE UPDATE ON retrospectives
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_theme_groups_updated_at BEFORE UPDATE ON theme_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_action_items_updated_at BEFORE UPDATE ON action_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT ALL ON ALL TABLES IN SCHEMA public TO neondb_owner;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO neondb_owner;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO neondb_owner;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- You can add sample data here if needed for testing

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

