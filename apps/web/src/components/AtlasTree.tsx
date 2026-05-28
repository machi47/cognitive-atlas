import type { AtlasTree as AtlasTreeType, AtlasTreeMap } from "../api/types";

export default function AtlasTree({ tree }: { tree?: AtlasTreeType }) {
  if (!tree || (!tree.uncategorized_maps.length && !tree.domains.length)) {
    return <p className="muted">Maps will appear after a thought is processed.</p>;
  }
  return (
    <div className="atlas-tree">
      {tree.domains.map((domain) => (
        <details key={domain.id} open>
          <summary>{domain.name}</summary>
          {domain.maps.map((map) => <MapRow key={map.id} map={map} />)}
        </details>
      ))}
      {tree.uncategorized_maps.map((map) => <MapRow key={map.id} map={map} />)}
    </div>
  );
}

function MapRow({ map }: { map: AtlasTreeMap }) {
  return (
    <div className="map-row">
      <a href={`/atlas/maps/${map.id}`}>{map.title}</a>
      <small>{map.node_count} nodes · {map.question_count} questions</small>
      {map.children.map((child) => <MapRow key={child.id} map={child} />)}
    </div>
  );
}

