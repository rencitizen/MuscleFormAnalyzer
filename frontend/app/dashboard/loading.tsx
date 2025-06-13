export default function Loading() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-4">
        {/* ヘッダースケルトン */}
        <div className="space-y-2">
          <div className="h-8 w-64 bg-muted animate-pulse rounded" />
          <div className="h-4 w-96 bg-muted animate-pulse rounded" />
        </div>

        {/* タブスケルトン */}
        <div className="h-10 w-full max-w-md bg-muted animate-pulse rounded" />

        {/* カードグリッドスケルトン */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="p-6 border rounded-lg space-y-3">
              <div className="flex justify-between items-start">
                <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                <div className="h-5 w-5 bg-muted animate-pulse rounded" />
              </div>
              <div className="h-8 w-20 bg-muted animate-pulse rounded" />
              <div className="h-3 w-32 bg-muted animate-pulse rounded" />
            </div>
          ))}
        </div>

        {/* 大きなカードスケルトン */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="lg:col-span-2 p-6 border rounded-lg">
            <div className="space-y-4">
              <div className="h-6 w-48 bg-muted animate-pulse rounded" />
              <div className="space-y-3">
                {[...Array(7)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="h-4 w-8 bg-muted animate-pulse rounded" />
                    <div className="flex-1 h-2 bg-muted animate-pulse rounded" />
                    <div className="h-4 w-12 bg-muted animate-pulse rounded" />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="p-6 border rounded-lg">
            <div className="space-y-4">
              <div className="h-6 w-32 bg-muted animate-pulse rounded" />
              {[...Array(3)].map((_, i) => (
                <div key={i} className="space-y-2">
                  <div className="h-4 w-full bg-muted animate-pulse rounded" />
                  <div className="h-3 w-24 bg-muted animate-pulse rounded" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}