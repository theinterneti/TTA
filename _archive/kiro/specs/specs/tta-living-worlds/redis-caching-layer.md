# Redis Caching Layer Spec (Focused)

## Purpose
Provide a high-level plan for Task 10: cache active world state, character states, and recent timeline events for performance. Ensure cache invalidation on updates and maintain consistency with Neo4j.

## Scope
- Cache keys and namespaces
- Data models to cache (world state snapshot, character states, recent events)
- Invalidation strategies (timeline event writes, world flag updates, entity mutations)
- Cache warming for frequently accessed elements
- Consistency policies (write-through vs. write-behind; TTLs; versioning)
- Observability (hit rate metrics, invalidation counters)

## Proposed Keyspace
- lw:world:{world_id}:state
- lw:world:{world_id}:flags
- lw:world:{world_id}:timeline:{entity_id}:recent
- lw:world:{world_id}:character:{char_id}:state
- lw:world:{world_id}:location:{loc_id}:state
- lw:world:{world_id}:object:{obj_id}:state

## Invalidation
- On timeline_engine.add_event: invalidate lw:world:{world_id}:timeline:{entity_id}:recent
- On world_state flag change: invalidate lw:world:{world_id}:flags
- On entity mutate (create/update/delete): invalidate corresponding state keys
- Use version increments lw:world:{world_id}:ver to coordinate readers

## Warming
- On world initialization or activation: prefill flags, world snapshot, and top-k recent events per active entity
- Background refresher updates popular timelines based on access metrics

## Consistency
- Prefer write-through for critical flags and world snapshot; write-behind acceptable for derived caches (recent events)
- Set TTLs for derived data; persistent keys (flags) without TTL but with versioning

## Observability
- Track metrics: cache_hits, cache_misses, invalidations, warm_count
- Expose a simple /metrics or logging counters for initial phase

## Testing
- Unit tests for key formatting and invalidation
- Integration tests asserting cache population, invalidation on event writes, and consistency with underlying data

## Risks / Open Questions
- Avoid caching sensitive player data; ensure privacy
- Ensure cache backpressure does not degrade persistence path
- Establish safe defaults when Redis unavailable


---
**Logseq:** [[TTA.dev/_archive/Kiro/Specs/Specs/Tta-living-worlds/Redis-caching-layer]]
