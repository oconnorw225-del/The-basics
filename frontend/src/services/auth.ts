import type { AuthUser } from '../types';

class AuthService {
  private currentUser: AuthUser | null = null;

  login(username: string, password: string): Promise<AuthUser> {
    return new Promise((resolve, reject) => {
      // Simulate API call
      setTimeout(() => {
        if (username && password) {
          const user: AuthUser = {
            id: '1',
            username,
            role: username === 'admin' ? 'admin' : 'user',
            permissions: username === 'admin' 
              ? ['read', 'write', 'delete', 'admin']
              : ['read'],
          };
          
          this.currentUser = user;
          localStorage.setItem('auth_token', 'mock-jwt-token');
          localStorage.setItem('user', JSON.stringify(user));
          resolve(user);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 500);
    });
  }

  logout() {
    this.currentUser = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  getCurrentUser(): AuthUser | null {
    if (this.currentUser) {
      return this.currentUser;
    }

    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        this.currentUser = JSON.parse(userStr);
        return this.currentUser;
      } catch {
        return null;
      }
    }

    return null;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  hasPermission(permission: string): boolean {
    const user = this.getCurrentUser();
    return user?.permissions.includes(permission) ?? false;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }
}

export default new AuthService();
