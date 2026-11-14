import HomeScreen from './_components/HomeScreen';

export default function Page({ searchParams }: { searchParams?: { project?: string; q?: string } }) {
  return <HomeScreen initialQuestion={searchParams?.q || ''} />;
}
