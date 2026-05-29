import { useQuery } from "@tanstack/react-query";
import { getLearnOverview, getLearnTextbook } from "../api/atlas";
import type { LearnBridge, LearnConcept, LearnContributor, LearnOverview, LearnQuestion, LearnTension } from "../api/types";

export default function AtlasPage() {
  const overview = useQuery({ queryKey: ["learn-overview"], queryFn: getLearnOverview });
  const textbook = useQuery({ queryKey: ["learn-textbook"], queryFn: getLearnTextbook });
  const data = overview.data;
  const sections = textbook.data?.sections || data?.textbook.sections || [];

  return (
    <section className="page-panel workbench-page">
      <div className="workbench-hero">
        <div>
          <p className="eyebrow">Global learning plane</p>
          <h1>Learn Workbench</h1>
          <p>
            Separate chats stay separate. This surface shows the shared technical understanding forming across all of them.
          </p>
        </div>
        {data && !data.empty ? (
          <div className="workbench-stat-strip">
            <Stat label="threads" value={data.topology.maps.length} />
            <Stat label="concepts" value={data.concepts.length} />
            <Stat label="questions" value={data.open_questions.length} />
            <Stat label="bridges" value={data.bridges.length} />
          </div>
        ) : null}
      </div>

      {overview.isLoading ? <p className="muted">Loading topology.</p> : null}
      {data?.empty ? (
        <p className="empty-state">No learning topology yet. Start a conversation and this will populate from extracted concepts, claims, questions, and bridges.</p>
      ) : null}

      {data && !data.empty ? (
        <div className="workbench-layout">
          <CurrentFrame data={data} />
          <LearningThreads data={data} />
          <SensemakingPanel data={data} />
          <BridgePanel bridges={data.bridges} />
          <TextbookPanel sections={sections} />
        </div>
      ) : null}
    </section>
  );
}

function CurrentFrame({ data }: { data: LearnOverview }) {
  const project = data.current_frame.project || strongestThreadTitle(data);
  const stack = data.current_frame.foundation_stack.length
    ? data.current_frame.foundation_stack
    : data.concepts.slice(0, 6).map((concept) => concept.label);
  return (
    <section className="workbench-band frame-band">
      <div>
        <p className="eyebrow">Current frame</p>
        <h2>{project || "No stable project frame yet"}</h2>
      </div>
      {stack.length ? (
        <div className="foundation-flow">
          {stack.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function LearningThreads({ data }: { data: LearnOverview }) {
  return (
    <section className="workbench-band">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Cross-conversation structure</p>
          <h2>Learning Threads</h2>
        </div>
        <small>Global by default. Chat titles below are provenance, not filters.</small>
      </div>
      <div className="learning-thread-list">
        {data.topology.maps.map((map) => {
          const concepts = data.concepts.filter((concept) => concept.map_id === map.id);
          const questions = data.open_questions.filter((question) => question.map_title === map.title);
          const tensions = data.tensions.filter((tension) => tension.node_labels.some((label) => concepts.some((concept) => concept.label === label)));
          const contributors = uniqueContributors(concepts.flatMap((concept) => concept.contributors));
          return (
            <article className="learning-thread" key={map.id}>
              <header>
                <div>
                  <h3>{map.title}</h3>
                  <p>{map.summary || "Conversation-derived technical thread."}</p>
                </div>
                <small>{map.concept_count} concepts · {map.relation_count} links · {map.question_count} questions</small>
              </header>
              <div className="thread-columns">
                <ThreadColumn title="What seems central" concepts={centralConcepts(concepts)} />
                <ThreadColumn title="Constraints and contracts" concepts={constraintConcepts(concepts)} />
                <ThreadWeakPoints tensions={tensions} questions={questions} />
              </div>
              <Contributors contributors={contributors} />
            </article>
          );
        })}
      </div>
    </section>
  );
}

function SensemakingPanel({ data }: { data: LearnOverview }) {
  const clarifications = data.concepts
    .filter((concept) => !["constraint"].includes(concept.node_type))
    .slice(0, 8);
  const questions = data.open_questions.slice(0, 6);
  const sourceNeeds = data.source_needs.slice(0, 5);

  return (
    <section className="workbench-band sensemaking-grid">
      <div className="synthesis-card">
        <p className="eyebrow">What the conversations clarified</p>
        <div className="insight-list">
          {clarifications.map((concept) => (
            <article key={concept.id} className="insight-row">
              <strong>{concept.label}</strong>
              <p>{concept.description || concept.node_type}</p>
              <div className="card-footer">
                <Status value={concept.epistemic_status} />
                <Contributors contributors={concept.contributors} />
              </div>
            </article>
          ))}
        </div>
      </div>
      <div className="synthesis-card">
        <p className="eyebrow">What should guide the next conversation</p>
        <ul className="question-stack">
          {questions.map((question) => (
            <li key={question.id}>
              <span>{question.question}</span>
              <Contributors contributors={question.contributors} />
            </li>
          ))}
          {sourceNeeds.map((need) => (
            <li key={need.id}>
              <span>{need.query}</span>
              <Status value={need.status} />
              <Contributors contributors={need.contributors} />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function BridgePanel({ bridges }: { bridges: LearnBridge[] }) {
  if (!bridges.length) return null;
  return (
    <section className="workbench-band">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Suggested, not forced</p>
          <h2>Bridges</h2>
        </div>
      </div>
      <div className="bridge-list">
        {bridges.slice(0, 6).map((bridge) => (
          <article className="bridge-row" key={bridge.id}>
            <div className="bridge-path">
              <span>{bridge.from_label}</span>
              <span>{"->"}</span>
              <span>{bridge.to_label}</span>
            </div>
            <p>{bridge.reason}</p>
            <div className="card-footer">
              <Status value={bridge.status} />
              <small>confidence {bridge.confidence.toFixed(2)}</small>
              <Contributors contributors={bridge.contributors} />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function TextbookPanel({ sections }: { sections: { title: string; body: string; bullets: string[] }[] }) {
  if (!sections.length) return null;
  return (
    <section className="workbench-band">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Conversation-derived</p>
          <h2>Personal Textbook</h2>
        </div>
      </div>
      <div className="textbook-sections">
        {sections.map((section) => (
          <article className="textbook-section" key={section.title}>
            <h3>{section.title}</h3>
            <p>{section.body}</p>
            <ul>
              {section.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}

function ThreadColumn({ title, concepts }: { title: string; concepts: LearnConcept[] }) {
  return (
    <div className="thread-column">
      <h4>{title}</h4>
      {concepts.length ? (
        <ul>
          {concepts.slice(0, 6).map((concept) => (
            <li key={concept.id}>
              <strong>{concept.label}</strong>
              <span>{concept.description || concept.node_type}</span>
              <Status value={concept.epistemic_status} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">Still forming.</p>
      )}
    </div>
  );
}

function ThreadWeakPoints({ tensions, questions }: { tensions: LearnTension[]; questions: LearnQuestion[] }) {
  return (
    <div className="thread-column">
      <h4>Weak points</h4>
      <ul>
        {tensions.slice(0, 3).map((tension) => (
          <li key={tension.id}>
            <strong>{tension.title}</strong>
            <span>{tension.description}</span>
          </li>
        ))}
        {questions.slice(0, 3).map((question) => (
          <li key={question.id}>
            <strong>Open question</strong>
            <span>{question.question}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <span>
      <strong>{value}</strong>
      <small>{label}</small>
    </span>
  );
}

function Status({ value }: { value: string }) {
  return <span className="status-pill">{value}</span>;
}

function Contributors({ contributors }: { contributors: LearnContributor[] }) {
  const unique = uniqueContributors(contributors);
  if (!unique.length) return null;
  return <small className="contributors">from {unique.map((item) => item.session_title).join(", ")}</small>;
}

function centralConcepts(concepts: LearnConcept[]) {
  return concepts.filter((concept) => !constraintTypes.has(concept.node_type)).slice(0, 8);
}

function constraintConcepts(concepts: LearnConcept[]) {
  return concepts.filter((concept) => constraintTypes.has(concept.node_type) || concept.label.toLowerCase().includes("constraint")).slice(0, 8);
}

function uniqueContributors(contributors: LearnContributor[]) {
  return Array.from(new Map(contributors.map((item) => [item.session_id, item])).values());
}

function strongestThreadTitle(data: LearnOverview) {
  return data.topology.maps[0]?.summary || data.topology.maps[0]?.title || null;
}

const constraintTypes = new Set(["constraint", "tension", "risk", "weak_point"]);
