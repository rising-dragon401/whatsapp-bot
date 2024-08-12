"use client";

import { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation'

const PaymentSuccess = () => {
  const searchParams = useSearchParams()
  const session_id = searchParams.get('session_id');

  const [data, setData] = useState(null);

  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return

    const fetchData = async () => {
      const response = await fetch(`/api/payment/success?session_id=${session_id}`);
      const data = await response.json();
      setData(data.message)
    }
    
    fetchData();
    hasRun.current = true;
  }, [session_id])

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="relative z-[-1] place-items-center before:absolute before:h-[300px] before:w-full before:-translate-x-1/2 before:rounded-full before:bg-gradient-radial before:from-white before:to-transparent before:blur-2xl before:content-[''] after:absolute after:-z-20 after:h-[180px] after:w-full after:translate-x-1/3 after:bg-gradient-conic after:from-sky-200 after:via-blue-200 after:blur-2xl after:content-[''] before:dark:bg-gradient-to-br before:dark:from-transparent before:dark:to-blue-700 before:dark:opacity-10 after:dark:from-sky-900 after:dark:via-[#0141ff] after:dark:opacity-40 sm:before:w-[480px] sm:after:w-[240px] before:lg:h-[360px]">
        <h1 className="mb-32 text-4xl font-bold">{data}</h1>
      </div>
    </main>
    
  );
}

export default PaymentSuccess