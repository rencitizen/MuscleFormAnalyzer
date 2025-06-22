// TENAX FIT v3.0 - Supabase Client Configuration
import { createClient } from '@supabase/supabase-js';
import type { Database } from '@/types/supabase';

// 環境変数チェック
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

// Supabaseクライアント作成（シングルトン）
export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    storage: typeof window !== 'undefined' ? window.localStorage : undefined,
    storageKey: 'tenax-fit-auth',
    flowType: 'pkce', // セキュアな認証フロー
  },
  global: {
    headers: {
      'x-application-name': 'tenax-fit-v3'
    }
  },
  db: {
    schema: 'public'
  },
  realtime: {
    params: {
      eventsPerSecond: 10 // レート制限
    }
  }
});

// 認証ヘルパー関数
export const auth = {
  // サインアップ
  async signUp(email: string, password: string, metadata?: any) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
        emailRedirectTo: `${window.location.origin}/auth/callback`
      }
    });
    
    if (error) throw error;
    return data;
  },

  // サインイン
  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    
    if (error) throw error;
    return data;
  },

  // Googleサインイン
  async signInWithGoogle() {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        scopes: 'profile email',
        queryParams: {
          access_type: 'offline',
          prompt: 'consent'
        }
      }
    });
    
    if (error) throw error;
    return data;
  },

  // サインアウト
  async signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },

  // 現在のユーザー取得
  async getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
  },

  // セッション取得
  async getSession() {
    const { data: { session } } = await supabase.auth.getSession();
    return session;
  },

  // パスワードリセット
  async resetPassword(email: string) {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`
    });
    
    if (error) throw error;
    return data;
  },

  // パスワード更新
  async updatePassword(newPassword: string) {
    const { data, error } = await supabase.auth.updateUser({
      password: newPassword
    });
    
    if (error) throw error;
    return data;
  }
};

// データベースヘルパー関数
export const db = {
  // ユーザープロフィール
  profiles: {
    async get(userId: string) {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single();
      
      if (error) throw error;
      return data;
    },

    async update(userId: string, updates: any) {
      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', userId)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }
  },

  // 分析結果
  analyses: {
    async create(analysis: any) {
      const { data, error } = await supabase
        .from('analyses')
        .insert(analysis)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    },

    async list(userId: string, limit = 10) {
      const { data, error } = await supabase
        .from('analyses')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(limit);
      
      if (error) throw error;
      return data;
    },

    async get(id: string) {
      const { data, error } = await supabase
        .from('analyses')
        .select('*')
        .eq('id', id)
        .single();
      
      if (error) throw error;
      return data;
    }
  },

  // トレーニング記録
  workouts: {
    async create(workout: any) {
      const { data, error } = await supabase
        .from('workouts')
        .insert(workout)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    },

    async list(userId: string, dateRange?: { from: Date; to: Date }) {
      let query = supabase
        .from('workouts')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false });

      if (dateRange) {
        query = query
          .gte('date', dateRange.from.toISOString())
          .lte('date', dateRange.to.toISOString());
      }

      const { data, error } = await query;
      
      if (error) throw error;
      return data;
    }
  }
};

// ストレージヘルパー関数
export const storage = {
  // 動画アップロード
  async uploadVideo(file: File, userId: string) {
    const fileName = `${userId}/${Date.now()}-${file.name}`;
    const { data, error } = await supabase.storage
      .from('videos')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (error) throw error;
    return data;
  },

  // 画像アップロード
  async uploadImage(file: File, userId: string, folder: string) {
    const fileName = `${userId}/${folder}/${Date.now()}-${file.name}`;
    const { data, error } = await supabase.storage
      .from('images')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (error) throw error;
    return data;
  },

  // ファイルURL取得
  getPublicUrl(bucket: string, path: string) {
    const { data } = supabase.storage
      .from(bucket)
      .getPublicUrl(path);
    
    return data.publicUrl;
  },

  // ファイル削除
  async deleteFile(bucket: string, path: string) {
    const { error } = await supabase.storage
      .from(bucket)
      .remove([path]);
    
    if (error) throw error;
  }
};

// リアルタイムサブスクリプション
export const realtime = {
  // チャンネル作成
  channel(name: string) {
    return supabase.channel(name);
  },

  // プレゼンス（オンライン状態）
  presence(channelName: string) {
    const channel = supabase.channel(channelName);
    return {
      track: (state: any) => channel.track(state),
      untrack: () => channel.untrack(),
      subscribe: (callback: (state: any) => void) => {
        channel.on('presence', { event: 'sync' }, () => {
          const state = channel.presenceState();
          callback(state);
        });
        return channel.subscribe();
      }
    };
  },

  // データベース変更の監視
  onDatabaseChange(
    table: string,
    filter?: { column: string; value: any },
    callback?: (payload: any) => void
  ) {
    let channel = supabase
      .channel(`db-changes-${table}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table,
          filter: filter ? `${filter.column}=eq.${filter.value}` : undefined
        },
        (payload) => {
          if (callback) callback(payload);
        }
      );

    return channel.subscribe();
  }
};

// エラーハンドリング
export class SupabaseError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'SupabaseError';
  }
}

// 型定義（仮）
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          email: string;
          username?: string;
          full_name?: string;
          avatar_url?: string;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['profiles']['Row'], 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['profiles']['Insert']>;
      };
      analyses: {
        Row: {
          id: string;
          user_id: string;
          video_url?: string;
          results: any;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['analyses']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['analyses']['Insert']>;
      };
      workouts: {
        Row: {
          id: string;
          user_id: string;
          date: string;
          exercises: any[];
          duration: number;
          notes?: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['workouts']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['workouts']['Insert']>;
      };
    };
  };
}