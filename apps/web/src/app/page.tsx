import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-black p-24">
      <h1 className="text-5xl font-bold tracking-tight text-white">Colossus</h1>
      <p className="mt-4 text-gray-400">Your self-hosted fitness tracker</p>
      <div className="mt-10 flex gap-4">
        <Link
          href="/exercises"
          className="rounded-lg border border-gray-700 px-6 py-3 text-sm font-semibold text-white hover:border-gray-500 hover:bg-gray-900"
        >
          Exercise Library
        </Link>
        <Link
          href="/templates"
          className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-black hover:bg-gray-200"
        >
          Workout Templates
        </Link>
      </div>
    </main>
  );
}
