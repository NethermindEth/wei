'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  RoadmapResponse, ViewType, RoadmapFilters, RoadmapStats,
  Intervention, Problem, FitnessFunction, Proposal
} from '@/types/roadmap';
import { getRoadmap, refreshRoadmap } from '@/services/roadmap';

interface RoadmapViewProps {
  protocolId: string;
  protocolName: string;
}

export function RoadmapView({ protocolId, protocolName }: RoadmapViewProps) {
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<ViewType>('timeline');
  const [filters, setFilters] = useState<RoadmapFilters>({
    search: '',
    streams: [],
    statuses: [],
    releases: [],
    severities: [],
    horizons: [],
  });

  // Initialize filters when roadmap loads
  useEffect(() => {
    if (roadmap && roadmap.streams && roadmap.interventions) {
      setFilters(prev => ({
        ...prev,
        streams: roadmap.streams,
        statuses: ['shipped', 'in_flight', 'planned', 'research'],
        releases: [...new Set(roadmap.interventions.map(i => i.release).filter((r): r is string => Boolean(r)))],
        severities: ['High', 'Medium', 'Low'],
        horizons: ['Now', 'Next', 'Later'],
      }));
    }
  }, [roadmap]);

  const loadRoadmap = useCallback(async (refresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const request = {
        subject: protocolName,
        kind: 'protocol' as const,
        scope: `Roadmap and development priorities for ${protocolName}`,
      };

      const result = refresh ? await refreshRoadmap(request) : await getRoadmap(request);
      setRoadmap(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load roadmap');
    } finally {
      setLoading(false);
    }
  }, [protocolName]);

  useEffect(() => {
    loadRoadmap();
  }, [protocolId, protocolName, loadRoadmap]);

  const stats: RoadmapStats = useMemo(() => {
    if (!roadmap || !roadmap.interventions || !roadmap.problems) return {
      totalInterventions: 0,
      totalProblems: 0,
      totalProposals: 0,
      byStatus: {},
      bySeverity: {},
      byHorizon: {},
    };

    const byStatus = roadmap.interventions.reduce((acc, item) => {
      acc[item.status] = (acc[item.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const bySeverity = roadmap.problems.reduce((acc, problem) => {
      acc[problem.severity] = (acc[problem.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const byHorizon = roadmap.problems.reduce((acc, problem) => {
      acc[problem.horizon] = (acc[problem.horizon] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalInterventions: roadmap.interventions.length,
      totalProblems: roadmap.problems.length,
      totalProposals: roadmap.proposals?.length || 0,
      byStatus,
      bySeverity,
      byHorizon,
    };
  }, [roadmap]);

  const filteredData = useMemo(() => {
    if (!roadmap || !roadmap.interventions || !roadmap.problems) return null;

    const filteredInterventions = roadmap.interventions.filter(item => {
      const matchesSearch = !filters.search || 
        [item.title, item.label, item.goal, item.stream].some(field => 
          field?.toLowerCase().includes(filters.search.toLowerCase())
        );
      const matchesStreams = filters.streams.length === 0 || filters.streams.includes(item.stream);
      const matchesStatuses = filters.statuses.length === 0 || filters.statuses.includes(item.status);
      const matchesReleases = filters.releases.length === 0 || (item.release && filters.releases.includes(item.release));
      
      return matchesSearch && matchesStreams && matchesStatuses && matchesReleases;
    });

    const filteredProblems = roadmap.problems.filter(problem => {
      const matchesSearch = !filters.search || 
        [problem.title, problem.target, problem.current, problem.stream].some(field => 
          field?.toLowerCase().includes(filters.search.toLowerCase())
        );
      const matchesStreams = filters.streams.length === 0 || filters.streams.includes(problem.stream);
      const matchesSeverities = filters.severities.length === 0 || filters.severities.includes(problem.severity);
      const matchesHorizons = filters.horizons.length === 0 || filters.horizons.includes(problem.horizon);
      
      return matchesSearch && matchesStreams && matchesSeverities && matchesHorizons;
    });

    return {
      ...roadmap,
      interventions: filteredInterventions,
      problems: filteredProblems,
    };
  }, [roadmap, filters]);

  if (loading && !roadmap) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/60 mx-auto mb-4"></div>
          <p className="text-white/60">Generating roadmap...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6 max-w-md mx-auto">
          <h3 className="text-red-400 font-semibold mb-2">Failed to load roadmap</h3>
          <p className="text-white/60 mb-4">{error}</p>
          <button
            onClick={() => loadRoadmap()}
            className="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-4 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-white/90 mb-2">No Roadmap Available</h2>
        <p className="text-white/60">Unable to generate roadmap for this protocol.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white/90 mb-2">
            {roadmap.domain?.name || 'Unknown'} Roadmap
          </h2>
          <p className="text-white/60 text-sm">
            {roadmap.domain?.scope || 'No scope defined'} • Generated {roadmap.domain?.as_of ? new Date(roadmap.domain.as_of).toLocaleDateString() : 'Unknown date'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => loadRoadmap(true)}
            disabled={loading}
            className="bg-white/10 hover:bg-white/20 text-white/90 px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
          <div className="text-2xl font-bold text-white/90">{stats.totalInterventions}</div>
          <div className="text-white/60 text-sm">Interventions</div>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
          <div className="text-2xl font-bold text-white/90">{stats.totalProblems}</div>
          <div className="text-white/60 text-sm">Problems</div>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
          <div className="text-2xl font-bold text-white/90">{stats.totalProposals}</div>
          <div className="text-white/60 text-sm">Proposals</div>
        </div>
        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
          <div className="text-2xl font-bold text-white/90">{roadmap.streams?.length || 0}</div>
          <div className="text-white/60 text-sm">Streams</div>
        </div>
      </div>

      {/* View Tabs */}
      <div className="border-b border-white/10">
        <nav className="flex space-x-8" aria-label="Roadmap Views">
          {[
            { id: 'timeline', label: 'Timeline' },
            { id: 'kanban', label: 'Kanban' },
            { id: 'matrix', label: 'Matrix' },
            { id: 'problems', label: 'Problems' },
            { id: 'proposals', label: 'Proposals' },
            { id: 'dependencies', label: 'Dependencies' },
          ].map((view) => (
            <button
              key={view.id}
              onClick={() => setActiveView(view.id as ViewType)}
              className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeView === view.id
                  ? 'border-[--color-accent] text-[--color-accent]'
                  : 'border-transparent text-white/60 hover:text-white/80 hover:border-white/20'
              }`}
            >
              {view.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Filters */}
      <div className="bg-white/5 border border-white/10 rounded-lg p-4">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-white/90 mb-2">Search</label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              placeholder="Search interventions, problems..."
              className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white/90 placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/20"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/90 mb-2">Streams</label>
            <div className="flex flex-wrap gap-2">
              {(roadmap.streams || []).map(stream => (
                <button
                  key={stream}
                  onClick={() => setFilters(prev => ({
                    ...prev,
                    streams: prev.streams.includes(stream)
                      ? prev.streams.filter(s => s !== stream)
                      : [...prev.streams, stream]
                  }))}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    filters.streams.includes(stream)
                      ? 'bg-white/20 text-white border-white/30'
                      : 'bg-white/5 text-white/60 border-white/20 hover:bg-white/10'
                  }`}
                >
                  {stream}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-white/90 mb-2">Status</label>
            <div className="flex flex-wrap gap-2">
              {['shipped', 'in_flight', 'planned', 'research'].map(status => (
                <button
                  key={status}
                  onClick={() => setFilters(prev => ({
                    ...prev,
                    statuses: prev.statuses.includes(status)
                      ? prev.statuses.filter(s => s !== status)
                      : [...prev.statuses, status]
                  }))}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    filters.statuses.includes(status)
                      ? 'bg-white/20 text-white border-white/30'
                      : 'bg-white/5 text-white/60 border-white/20 hover:bg-white/10'
                  }`}
                >
                  {status.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-white/90 mb-2">Severity</label>
            <div className="flex flex-wrap gap-2">
              {['High', 'Medium', 'Low'].map(severity => (
                <button
                  key={severity}
                  onClick={() => setFilters(prev => ({
                    ...prev,
                    severities: prev.severities.includes(severity)
                      ? prev.severities.filter(s => s !== severity)
                      : [...prev.severities, severity]
                  }))}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    filters.severities.includes(severity)
                      ? 'bg-white/20 text-white border-white/30'
                      : 'bg-white/5 text-white/60 border-white/20 hover:bg-white/10'
                  }`}
                >
                  {severity}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="min-h-[400px]">
        {activeView === 'timeline' && <TimelineView data={filteredData} />}
        {activeView === 'kanban' && <KanbanView data={filteredData} />}
        {activeView === 'matrix' && <MatrixView data={filteredData} />}
        {activeView === 'problems' && <ProblemsView data={filteredData} />}
        {activeView === 'proposals' && <ProposalsView data={filteredData} />}
        {activeView === 'dependencies' && <DependenciesView data={filteredData} />}
      </div>
    </div>
  );
}

// View Components
function TimelineView({ data }: { data: RoadmapResponse | null }) {
  if (!data || !data.interventions) return <div className="text-center py-8 text-white/60">No data available</div>;

  const timeframes = [...new Set(data.interventions.map(i => i.timeframe).filter(Boolean))].sort();

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[800px]">
        <div className="grid" style={{ gridTemplateColumns: `200px repeat(${timeframes.length}, minmax(200px, 1fr))` }}>
          <div></div>
          {timeframes.map(timeframe => (
            <div key={timeframe} className="sticky top-0 z-10 bg-[#0b0f14]/80 backdrop-blur border-b border-white/10 p-3 text-sm font-semibold text-white/90">
              {timeframe}
            </div>
          ))}
        </div>
        {data.streams.map(stream => (
          <div key={stream} className="grid items-start" style={{ gridTemplateColumns: `200px repeat(${timeframes.length}, minmax(200px, 1fr))` }}>
            <div className="sticky left-0 z-10 bg-[#0b0f14]/80 backdrop-blur border-r border-white/10 p-3">
              <div className="font-medium text-white/90">{stream}</div>
            </div>
            {timeframes.map(timeframe => (
              <div key={timeframe} className="border-b border-white/5 p-3">
                <div className="space-y-3">
                  {data.interventions
                    .filter(i => i.stream === stream && i.timeframe === timeframe)
                    .map(intervention => (
                      <InterventionCard key={intervention.id} intervention={intervention} />
                    ))}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function KanbanView({ data }: { data: RoadmapResponse | null }) {
  if (!data || !data.interventions) return <div className="text-center py-8 text-white/60">No data available</div>;

  const columns = ['shipped', 'in_flight', 'planned', 'research'];

  return (
    <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
      {columns.map(status => (
        <div key={status} className="bg-white/5 border border-white/10 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white/90 capitalize">{status.replace('_', ' ')}</h3>
            <span className="text-xs text-white/60 bg-white/10 px-2 py-1 rounded">
              {data.interventions.filter(i => i.status === status).length}
            </span>
          </div>
          <div className="space-y-3">
            {data.interventions
              .filter(i => i.status === status)
              .map(intervention => (
                <InterventionCard key={intervention.id} intervention={intervention} />
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function MatrixView({ data }: { data: RoadmapResponse | null }) {
  if (!data || !data.interventions) return <div className="text-center py-8 text-white/60">No data available</div>;

  const releases = [...new Set(data.interventions.map(i => i.release).filter(Boolean))];

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-separate border-spacing-0 min-w-[600px]">
        <thead>
          <tr>
            <th className="sticky left-0 bg-[#0b0f14]/80 backdrop-blur z-10 text-left p-3 text-sm font-semibold border-b border-white/10 text-white/90">
              Stream
            </th>
            {releases.map(release => (
              <th key={release} className="text-left p-3 text-sm font-semibold border-b border-white/10 text-white/90">
                {release}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.streams.map(stream => (
            <tr key={stream}>
              <td className="sticky left-0 bg-[#0b0f14]/80 backdrop-blur z-10 p-3 border-b border-white/5 font-medium text-white/90">
                {stream}
              </td>
              {releases.map(release => (
                <td key={release} className="align-top p-3 border-b border-white/5">
                  <div className="space-y-2">
                    {data.interventions
                      .filter(i => i.stream === stream && i.release === release)
                      .map(intervention => (
                        <InterventionCard key={intervention.id} intervention={intervention} />
                      ))}
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProblemsView({ data }: { data: RoadmapResponse | null }) {
  if (!data || !data.problems || !data.fitness_functions) return <div className="text-center py-8 text-white/60">No data available</div>;

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-white/90">Problems</h3>
        <div className="space-y-3">
          {data.problems.map(problem => (
            <ProblemCard key={problem.id} problem={problem} />
          ))}
        </div>
      </div>
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-white/90">Fitness Functions</h3>
        <div className="space-y-3">
          {data.fitness_functions.map(ff => (
            <FitnessFunctionCard key={ff.id} fitnessFunction={ff} />
          ))}
        </div>
      </div>
    </div>
  );
}

function ProposalsView({ data }: { data: RoadmapResponse | null }) {
  if (!data || !data.proposals) return <div className="text-center py-8 text-white/60">No proposals available</div>;

  const stages = ['Draft', 'Review', 'Vote', 'Approved', 'Implementing', 'Done'];

  return (
    <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
      {stages.map(stage => (
        <div key={stage} className="bg-white/5 border border-white/10 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white/90">{stage}</h3>
            <span className="text-xs text-white/60 bg-white/10 px-2 py-1 rounded">
              {data.proposals!.filter(p => p.stage === stage).length}
            </span>
          </div>
          <div className="space-y-3">
            {data.proposals!
              .filter(p => p.stage === stage)
              .map(proposal => (
                <ProposalCard key={proposal.id} proposal={proposal} />
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function DependenciesView({ data }: { data: RoadmapResponse | null }) {
  if (!data || !data.interventions) return <div className="text-center py-8 text-white/60">No data available</div>;

  // Simple dependency visualization
  const interventionsWithDeps = data.interventions.filter(i => i.deps && i.deps.length > 0);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white/90">Dependencies</h3>
      <div className="space-y-3">
        {interventionsWithDeps.map(intervention => (
          <div key={intervention.id} className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="font-medium text-white/90 mb-2">{intervention.title}</div>
            <div className="text-sm text-white/60">
              Depends on: {intervention.deps!.map(depId => {
                const dep = data.interventions.find(i => i.id === depId);
                return dep ? dep.title : depId;
              }).join(', ')}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Card Components
function InterventionCard({ intervention }: { intervention: Intervention }) {
  const statusColors = {
    shipped: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    in_flight: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    planned: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    research: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    abandoned: 'bg-red-500/20 text-red-400 border-red-500/30',
    stale: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    unclear: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-3 hover:bg-white/10 transition-colors">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <div className="font-medium text-white/90 text-sm leading-tight">{intervention.title}</div>
          {intervention.label && (
            <div className="text-xs text-white/60 mt-1">{intervention.label}</div>
          )}
        </div>
        <span className={`px-2 py-1 rounded-full text-xs border ${statusColors[intervention.status as keyof typeof statusColors]}`}>
          {intervention.status.replace('_', ' ')}
        </span>
      </div>
      <div className="flex flex-wrap gap-2 mb-2">
        <span className="px-2 py-1 bg-white/10 text-white/70 text-xs rounded">
          {intervention.stream}
        </span>
        {intervention.release && (
          <span className="px-2 py-1 bg-white/10 text-white/70 text-xs rounded">
            {intervention.release}
          </span>
        )}
      </div>
      {intervention.goal && (
        <p className="text-xs text-white/60 leading-relaxed">{intervention.goal}</p>
      )}
    </div>
  );
}

function ProblemCard({ problem }: { problem: Problem }) {
  const severityColors = {
    High: 'bg-red-500/20 text-red-400 border-red-500/30',
    Medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    Low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex-1 min-w-0">
          <div className="font-medium text-white/90 leading-tight">{problem.title}</div>
        </div>
        <div className="flex gap-2">
          <span className={`px-2 py-1 rounded-full text-xs border ${severityColors[problem.severity as keyof typeof severityColors]}`}>
            {problem.severity}
          </span>
          <span className="px-2 py-1 bg-white/10 text-white/70 text-xs rounded">
            {problem.horizon}
          </span>
        </div>
      </div>
      <div className="space-y-2 text-sm">
        <div>
          <span className="text-white/60">Target:</span>
          <span className="text-white/90 ml-2">{problem.target}</span>
        </div>
        <div>
          <span className="text-white/60">Current:</span>
          <span className="text-white/90 ml-2">{problem.current}</span>
        </div>
        <div>
          <span className="text-white/60">Exit criteria:</span>
          <span className="text-white/90 ml-2">{problem.exit_criteria}</span>
        </div>
      </div>
    </div>
  );
}

function FitnessFunctionCard({ fitnessFunction }: { fitnessFunction: FitnessFunction }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
      <div className="font-medium text-white/90 mb-2">{fitnessFunction.name}</div>
      <div className="text-sm text-white/60 mb-2">{fitnessFunction.description}</div>
      <div className="flex items-center gap-4 text-xs">
        <span className="text-white/60">Direction:</span>
        <span className="text-white/90">{fitnessFunction.direction}</span>
        {fitnessFunction.unit && (
          <>
            <span className="text-white/60">Unit:</span>
            <span className="text-white/90">{fitnessFunction.unit}</span>
          </>
        )}
      </div>
    </div>
  );
}

function ProposalCard({ proposal }: { proposal: Proposal }) {
  const stageColors = {
    Draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    Review: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    Vote: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    Approved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    Implementing: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    Done: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-3">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="font-medium text-white/90 text-sm leading-tight">{proposal.title}</div>
        <span className={`px-2 py-1 rounded-full text-xs border ${stageColors[proposal.stage as keyof typeof stageColors]}`}>
          {proposal.stage}
        </span>
      </div>
      {proposal.owner && (
        <div className="text-xs text-white/60">Owner: {proposal.owner}</div>
      )}
      {proposal.notes && (
        <div className="text-xs text-white/60 mt-2">{proposal.notes}</div>
      )}
    </div>
  );
}
