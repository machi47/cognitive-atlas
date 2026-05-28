import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getAtlasTree } from "../api/atlas";
import AtlasTree from "../components/AtlasTree";

export default function AtlasPage() {
  const params = useParams();
  const tree = useQuery({ queryKey: ["atlas-tree"], queryFn: getAtlasTree });
  return (
    <section className="page-panel atlas-page">
      <h1>Memory</h1>
      {params.mapId && <p className="muted">Map selected: {params.mapId}</p>}
      <AtlasTree tree={tree.data} />
    </section>
  );
}
