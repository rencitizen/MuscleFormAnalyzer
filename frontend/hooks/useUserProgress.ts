import { useState, useEffect } from 'react';
import { useAuth } from '../components/providers/AuthProvider';
import { ProgressService, ProgressData, ProgressSummary } from '../lib/services/progressService';

interface UseUserProgressOptions {
  exerciseFilter?: string;
  dateFrom?: Date;
  dateTo?: Date;
  realtime?: boolean;
}

interface UseUserProgressReturn {
  progressData: ProgressData[];
  summary: ProgressSummary | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * ユーザー固有の進捗データを取得するカスタムフック
 */
export const useUserProgress = (options: UseUserProgressOptions = {}): UseUserProgressReturn => {
  const { user } = useAuth();
  const [progressData, setProgressData] = useState<ProgressData[]>([]);
  const [summary, setSummary] = useState<ProgressSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const { exerciseFilter, dateFrom, dateTo, realtime = true } = options;

  // データ取得関数
  const fetchData = async () => {
    if (!user) {
      setProgressData([]);
      setSummary(null);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // 進捗データ取得
      const data = await ProgressService.getUserProgress(exerciseFilter, dateFrom, dateTo);
      setProgressData(data);

      // サマリー取得
      const summaryData = await ProgressService.getProgressSummary(dateFrom);
      setSummary(summaryData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('データ取得に失敗しました'));
      setProgressData([]);
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  };

  // 初回データ取得
  useEffect(() => {
    fetchData();
  }, [user, exerciseFilter, dateFrom?.getTime(), dateTo?.getTime()]);

  // リアルタイム監視
  useEffect(() => {
    if (!user || !realtime) return;

    const unsubscribe = ProgressService.subscribeToUserProgress(
      (data) => {
        // フィルタリング適用
        let filteredData = data;
        if (dateFrom) {
          filteredData = filteredData.filter(item => 
            new Date(item.date) >= dateFrom
          );
        }
        if (dateTo) {
          filteredData = filteredData.filter(item => 
            new Date(item.date) <= dateTo
          );
        }

        setProgressData(filteredData);
        
        // サマリーも更新
        ProgressService.getProgressSummary(dateFrom).then(setSummary);
      },
      exerciseFilter
    );

    return () => unsubscribe();
  }, [user, exerciseFilter, dateFrom?.getTime(), dateTo?.getTime(), realtime]);

  return {
    progressData,
    summary,
    isLoading,
    error,
    refetch: fetchData
  };
};