from app.controller.model.Sesion import Sesion


class GestorChatBot:
    """
    Gestor encargado de procesar los comandos introducidos en el ChatBot.
    Valida la sintaxis, delega la lógica a los gestores de dominio y
    genera la respuesta textual que se devuelve a la vista.
    """

    def __init__(self, gestor_especies, gestor_equipos):
        """
        Inicializa el gestor con las dependencias necesarias.
        """
        self.gestor_especies = gestor_especies
        self.gestor_equipos = gestor_equipos

        # Número de argumentos requeridos por cada comando
        self.comandos = {
            "/stats": 1,
            "/weaknesses": 1,
            "/evolution": 1,
            "/score_team": 1,
            "/compare": 2,
        }

    def procesarComando(self, pComando: str) -> str:
        """
        Procesa el comando introducido por el usuario y devuelve
        la respuesta correspondiente en formato texto.
        """
        comando = (pComando or "").strip()

        # 1B: Mensaje vacío o solo espacios
        if not comando:
            return "No se puede enviar."

        # 1E / 1F: Falta el símbolo '/' al inicio
        if not comando.startswith("/"):
            return "Error de sintaxis. Falta el icono de inicio de comando '/'."

        partes = comando.split()
        cmd = partes[0]
        args = partes[1:]

        # 1C: Comando incompleto (solo "/")
        if cmd == "/":
            comandos_disponibles = ", ".join(sorted(self.comandos.keys()))
            return (
                "Error de sintaxis. Falta el comando. Muestra los comandos posibles. "
                f"Comandos: {comandos_disponibles}"
            )

        # 1D: Comando inexistente
        if cmd not in self.comandos:
            return "Error de sintaxis. Comando no encontrado."

        # Gestión específica del comando /compare (casos 6G y 6H)
        if cmd == "/compare":
            if len(args) == 0:
                return "Error de sintaxis. Faltan los argumentos."
            if len(args) == 1:
                return "Error de sintaxis. Falta un argumento."
            if len(args) > 2:
                return "Error de sintaxis. Demasiados argumentos."
            try:
                return self._cmd_compare(args[0], args[1])
            except Exception:
                return "Error interno. Inténtalo más tarde."

        # Resto de comandos (todos requieren un único argumento)
        n_req = self.comandos[cmd]
        if len(args) < n_req:
            return "Error de sintaxis. Falta el argumento."
        if len(args) > n_req:
            return "Error de sintaxis. Demasiados argumentos."

        # Delegación al método correspondiente
        try:
            if cmd == "/stats":
                return self._cmd_stats(args[0])
            if cmd == "/weaknesses":
                return self._cmd_weaknesses(args[0])
            if cmd == "/evolution":
                return self._cmd_evolution(args[0])
            if cmd == "/score_team":
                return self._cmd_score_team(args[0])
            return "Error interno."
        except Exception:
            return "Error interno. Inténtalo más tarde."

    # --------------------------------------------------
    # Métodos auxiliares
    # --------------------------------------------------

    def _as_dict(self, row):
        """
        Garantiza que una fila devuelta por la BD se trate como diccionario.
        """
        return row if isinstance(row, dict) else dict(row)

    def _total_stats(self, pk: dict) -> int:
        """
        Calcula la suma total de estadísticas de un Pokémon.
        """
        return sum(
            [
                pk.get("PS") or 0,
                pk.get("Ataque") or 0,
                pk.get("Defensa") or 0,
                pk.get("AtaqueEspecial") or 0,
                pk.get("DefensaEspecial") or 0,
                pk.get("Velocidad") or 0,
            ]
        )

    # --------------------------------------------------
    # Implementación de comandos
    # --------------------------------------------------

    def _cmd_stats(self, nombre_pokemon: str) -> str:
        """
        Devuelve las estadísticas de un Pokémon.
        """
        p = self.gestor_especies.getPokemonPorNombre(nombre_pokemon)
        if not p:
            return "Pokemon no encontrado."

        return (
            f"{p.get('Nombre')} "
            f"(PS {p.get('PS')}, Atq {p.get('Ataque')}, Def {p.get('Defensa')}, "
            f"AtqEsp {p.get('AtaqueEspecial')}, DefEsp {p.get('DefensaEspecial')}, "
            f"Vel {p.get('Velocidad')})."
        )

    def _cmd_compare(self, p1: str, p2: str) -> str:
        """
        Compara dos Pokémon en base a la suma de sus estadísticas.
        """
        a = self.gestor_especies.getPokemonPorNombre(p1)
        b = self.gestor_especies.getPokemonPorNombre(p2)

        if not a and not b:
            return "Pokémons no encontrados."
        if not a:
            return "Pokemon 1 no encontrado."
        if not b:
            return "Pokemon 2 no encontrado."

        ta = self._total_stats(a)
        tb = self._total_stats(b)

        if ta > tb:
            ganador = a.get("Nombre")
        elif tb > ta:
            ganador = b.get("Nombre")
        else:
            ganador = "Empate"

        return (
            f"Comparación {a.get('Nombre')} vs {b.get('Nombre')}: "
            f"Total {ta} vs {tb}. Resultado: {ganador}."
        )

    def _cmd_weaknesses(self, especie: str) -> str:
        """
        Muestra debilidades y fortalezas de una especie.
        """
        info = self.gestor_especies.getDebilidadesYFortalezasPorEspecie(especie)
        if info is None:
            return "Pokemon no encontrado."

        tipos = info.get("tipos", [])
        deb = info.get("debilidades", [])
        fort = info.get("fortalezas", [])

        if not tipos:
            return f"{especie}: No hay datos de tipos en la base de datos."

        return (
            f"{especie} (Tipos: {', '.join(tipos)}). "
            f"Débil contra: {', '.join(deb) if deb else 'Ninguno'}. "
            f"Fuerte contra: {', '.join(fort) if fort else 'Ninguno'}."
        )

    def _cmd_evolution(self, especie: str) -> str:
        """
        Devuelve la cadena evolutiva de una especie.
        """
        cadena = self.gestor_especies.getCadenaEvolutivaPorEspecie(especie)
        if cadena is None:
            return "Pokemon no encontrado."
        if not cadena:
            return "No tiene cadena evolutiva."

        return "Cadena evolutiva: " + " -> ".join(cadena)

    def _cmd_score_team(self, nombre_equipo: str) -> str:
        """
        Calcula la puntuación total y media de un equipo Pokémon.
        """
        equipo = None

        # 1) Equipos del usuario logueado
        sesion = Sesion().getSession()
        id_usuario = None
        if sesion:
            id_usuario = sesion.get("IDUsuario") or sesion.get("idUsuario") or sesion.get("ID")

        if id_usuario:
            equipos = self.gestor_equipos.getEquiposUsuario(id_usuario) or []
            for e in equipos:
                e = self._as_dict(e)
                if (e.get("Nombre") or "").lower() == nombre_equipo.lower():
                    equipo = e
                    break

        # 2) Fallback: equipo global (seed)
        if not equipo and hasattr(self.gestor_equipos, "getEquipoPorNombre"):
            equipo = self.gestor_equipos.getEquipoPorNombre(nombre_equipo)

        if not equipo:
            return "Equipo no encontrado."

        pokes = self.gestor_equipos.getPokemonEquipo(equipo["IDEquipo"]) or []
        if not pokes:
            return f"El equipo '{equipo.get('Nombre')}' está vacío."

        total = 0
        n = 0
        detalle = []

        for pk in pokes:
            pk = self._as_dict(pk)
            nombre_pk = pk.get("Nombre")
            if not nombre_pk:
                continue

            stats = self.gestor_especies.getPokemonPorNombre(nombre_pk)
            if not stats:
                continue

            puntos = self._total_stats(stats)
            total += puntos
            n += 1
            detalle.append(f"{stats.get('Nombre')}={puntos}")

        if n == 0:
            return f"No hay estadísticas disponibles para evaluar el equipo '{equipo.get('Nombre')}'."

        media = total // n
        return (
            f"Equipo '{equipo.get('Nombre')}' evaluado: "
            f"{n} Pokémon, puntuación total {total}, media {media}. "
            f"({', '.join(detalle)})"
        )
