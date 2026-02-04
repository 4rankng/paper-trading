const SESSION_STORAGE_KEY = 'termai_session_id';

export class Storage {
  static getSessionId(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(SESSION_STORAGE_KEY);
  }

  static setSessionId(id: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(SESSION_STORAGE_KEY, id);
  }

  static clearSessionId(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(SESSION_STORAGE_KEY);
  }

  static async validateSession(sessionId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `/api/session?action=validate&id=${encodeURIComponent(sessionId)}`
      );
      const data = await response.json();
      return data.valid === true;
    } catch (error) {
      console.error('Failed to validate session:', error);
      return false;
    }
  }

  static async createSession(): Promise<string> {
    try {
      const response = await fetch('/api/session?action=create');
      const data = await response.json();
      if (data.session_id) {
        this.setSessionId(data.session_id);
        return data.session_id;
      }
      throw new Error('Failed to create session');
    } catch (error) {
      console.error('Failed to create session:', error);
      throw error;
    }
  }

  static async getOrCreateSession(): Promise<string> {
    const existingId = this.getSessionId();
    if (existingId) {
      return existingId; // Trust localStorage, skip validation for faster load
    }
    return this.createSession();
  }
}
