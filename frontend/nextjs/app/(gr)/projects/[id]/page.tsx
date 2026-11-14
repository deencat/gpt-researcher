import ProjectDetailScreen from '../../_components/ProjectDetailScreen';

export default function ProjectPage({ params }: { params: { id: string } }) {
  return <ProjectDetailScreen projectId={params.id} />;
}
