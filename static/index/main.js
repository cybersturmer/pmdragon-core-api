const app = Vue.createApp({
    data() {
        return {
            defaultEnvAlias: "linux",
            envs: [
                {
                    title: "Linux",
                    alias: "linux",
                    icon: "fab fa-linux fa-lg"
                },
                {
                    title: "MacOs",
                    alias: "macos",
                    icon: "fab fa-apple fa-lg"
                },
                {
                    title: "Windows",
                    alias: "windows",
                    icon: "fab fa-windows fa-lg"
                }
            ]
        }
    },
    computed: {
        releases () {
            return $releases
        },
        version () {
            return $version
        },
        timestamp () {
            return $timestamp
        }
    }
})