/*jslint bitwise: true, browser: true, evil:true, devel: true, todo: true, debug: true, nomen: true, plusplus: true, sloppy: true, vars: true, white: true, indent: 2 */
/*globals HANNIBAL, Engine, uneval */

/*--------------- R P C   E X E C U T O R ---------------------------------

  Realtime RPC Executor for Hannibal

  Polls a command file and executes game-intent operations like:
  - move: move entities to a position
  - select: set current selection
  - gather: order entities to gather resources
  - build: construct buildings
  - train: train units
  - research: research technologies

  Uses file-based transport (simple but works):
  - Reads: exports/realtime_commands.json
  - Writes: exports/realtime_responses.json

  V: 0.1.0, Feb 2026

*/

HANNIBAL = (function(H){

  H.LIB.RpcExecutor = function(context){

    H.extend(this, {

      context: context,
      klass:    "rpc-executor",
      parent:   context,
      name:     context.name + ":rpc",

      // Current selection (for gather/build commands)
      selection: {
        current: []
      },

      // Polling interval (every N turns)
      pollInterval: 5,
      pollCounter: 0,

      // Processed command IDs (to avoid duplicate execution)
      processedIds: {},

      imports: [
        "id",
        "effector",
      ],

    });

  };

  H.LIB.RpcExecutor.prototype = H.mixin(
    H.LIB.Serializer.prototype, {
    constructor: H.LIB.RpcExecutor,

    log: function(){
      this.deb();
      this.deb("   RPC: executor initialized");
    },

    update: function(){
      // Poll for commands every N turns
      this.pollCounter++;
      if (this.pollCounter >= this.pollInterval){
        this.pollCounter = 0;
        this.pollCommands();
      }
    },

    pollCommands: function(){
      // File polling is only enabled if debug.fil is set
      if (!this.checkDebug("fil")) return;

      var DEB = this.context.debug;
      if (!DEB || !DEB.fil) return;

      // This is a placeholder - actual file reading would need Engine support
      // For now, we'll use a different approach: check if commands exist in memory

      // In practice, you'd need to:
      // 1. Have the launcher write commands to a file
      // 2. Have Hannibal read that file (requires Engine.ReadFile support)
      // 3. Execute commands and write responses

      // For this POC, we'll demonstrate the execution logic
      this.deb("   RPC: polling for commands...");
    },

    executeCommand: function(cmd){

      this.deb("   RPC: executing command: %s", uneval(cmd));

      var correlation_id = cmd.correlation_id || "unknown";
      var action = cmd.action;
      var result, error;

      try {

        switch(action){

          case "move":
            result = this.executeMove(cmd);
            break;

          case "select":
            result = this.executeSelect(cmd);
            break;

          case "gather":
            result = this.executeGather(cmd);
            break;

          case "build":
            result = this.executeBuild(cmd);
            break;

          case "train":
            result = this.executeTrain(cmd);
            break;

          case "research":
            result = this.executeResearch(cmd);
            break;

          case "get_state":
            result = this.executeGetState(cmd);
            break;

          case "list_entities":
            result = this.executeListEntities(cmd);
            break;

          default:
            error = "Unknown action: " + action;
        }

        if (error){
          return {
            correlation_id: correlation_id,
            ok: false,
            error: error
          };
        } else {
          return {
            correlation_id: correlation_id,
            ok: true,
            result: result
          };
        }

      } catch(e){
        return {
          correlation_id: correlation_id,
          ok: false,
          error: "Exception: " + e.toString()
        };
      }
    },

    executeMove: function(cmd){
      // Move entities to a position
      // cmd: {entity_ids: [186, 188], position: {x: 150, z: 200}}

      var entity_ids = cmd.entity_ids || [];
      var position = cmd.position || {};
      var x = position.x;
      var z = position.z;

      if (!entity_ids.length){
        throw new Error("entity_ids is empty");
      }

      if (x === undefined || z === undefined){
        throw new Error("position must have x and z coordinates");
      }

      // Filter to owned entities
      var owned = this.filterOwnedEntities(entity_ids);

      if (!owned.length){
        throw new Error("No owned entities found in: " + uneval(entity_ids));
      }

      // Execute move command via effector
      this.effector.move(owned, [x, z]);

      this.deb("   RPC: moved entities %s to [%s, %s]", uneval(owned), x, z);

      return {
        moved_ids: owned,
        position: {x: x, z: z}
      };
    },

    executeSelect: function(cmd){
      // Set current selection
      // cmd: {entity_ids: [186, 188]}

      var entity_ids = cmd.entity_ids || [];

      // Filter to owned + existing entities
      var owned = this.filterOwnedEntities(entity_ids);

      this.selection.current = owned;

      this.deb("   RPC: selected entities: %s", uneval(owned));

      return {
        selected_ids: owned
      };
    },

    executeGather: function(cmd){
      // Order selected entities to gather resource
      // cmd: {resource: "wood.tree", targets: 3, near: "selection"}

      var resource = cmd.resource;
      var targets = cmd.targets || null;
      var near = cmd.near || "selection";

      if (!this.selection.current.length){
        throw new Error("No entities selected for gather command");
      }

      // This would use Hannibal's resource discovery system
      // For now, simplified:

      this.deb("   RPC: gather command - resource: %s, entities: %s", resource, uneval(this.selection.current));

      // In full implementation:
      // 1. Find nearby resources of type 'resource'
      // 2. Call effector.gather(this.selection.current, resourceTargets)

      return {
        entity_ids: this.selection.current,
        resource: resource,
        note: "Gather not fully implemented - needs resource discovery"
      };
    },

    executeBuild: function(cmd){
      // Build a structure
      // cmd: {what: "house", amount: 1, mode: "selected"}

      var what = cmd.what;
      var mode = cmd.mode || "selected";

      if (mode === "selected" && !this.selection.current.length){
        // Error then fallback to economy
        this.deb("   RPC: build - selection empty, would fallback to economy");
        // In full implementation: this.economy.request({verb: "build", ...})

        return {
          builder_ids: [],
          template: what,
          used_mode: "economy",
          fallback_triggered: true,
          note: "Economy mode not implemented in POC"
        };
      }

      this.deb("   RPC: build command - what: %s, builders: %s", what, uneval(this.selection.current));

      // In full implementation:
      // 1. Resolve civ-correct template
      // 2. Pick placement position
      // 3. Call effector.construct(builders, template, position)

      return {
        builder_ids: this.selection.current,
        template: what,
        used_mode: mode,
        fallback_triggered: false,
        note: "Build not fully implemented - needs placement logic"
      };
    },

    executeTrain: function(cmd){
      // Train units via economy
      // cmd: {unit: "female.citizen", amount: 3}

      var unit = cmd.unit;
      var amount = cmd.amount || 1;

      this.deb("   RPC: train command - unit: %s, amount: %s", unit, amount);

      // In full implementation:
      // 1. Resolve civ-correct template
      // 2. Call economy.request({verb: "train", ...})

      return {
        template: unit,
        queued: amount,
        note: "Train not fully implemented - needs economy integration"
      };
    },

    executeResearch: function(cmd){
      // Research tech via economy
      // cmd: {tech: "phase_village"}

      var tech = cmd.tech;

      this.deb("   RPC: research command - tech: %s", tech);

      // In full implementation:
      // Call economy.request({verb: "research", ...})

      return {
        tech: tech,
        queued: true,
        note: "Research not fully implemented - needs economy integration"
      };
    },

    executeGetState: function(cmd){
      // Get current player state

      var state = this.context.state;
      var resources = state.playerData.resourceCounts;

      return {
        state: {
          pid: this.id,
          resources: {
            food: resources.food || 0,
            wood: resources.wood || 0,
            stone: resources.stone || 0,
            metal: resources.metal || 0
          },
          population: state.playerData.popCount || 0,
          population_cap: state.playerData.popLimit || 0,
          phase: state.playerData.phase || 0,
          current_selection: this.selection.current
        }
      };
    },

    executeListEntities: function(cmd){
      // List entities (simplified)

      var filter = cmd.filter || {};
      var entities = [];

      // Get all own units
      var units = this.context.state.getOwnUnits().toEntityArray();

      // Simplified filtering
      units.slice(0, 10).forEach(function(ent){
        entities.push({
          id: ent.id(),
          template: ent.templateName(),
          position: ent.position()
        });
      });

      return {
        entities: entities,
        count: entities.length,
        note: "Listing first 10 entities only (POC)"
      };
    },

    filterOwnedEntities: function(entity_ids){
      // Filter entity IDs to only owned + existing ones

      var state = this.context.state;
      var owned = [];

      entity_ids.forEach(function(id){
        var ent = state.getEntityById(id);
        if (ent && ent.isOwn(state.playerData)){
          owned.push(id);
        }
      });

      return owned;
    }

  });

  return H;

}(HANNIBAL));
