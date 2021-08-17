const app = Vue.createApp({
    data() {
        return {
            releases: {},
            version: null,
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
        linuxReleases () {
            try {
                return this.releases.linux
            } catch (e) {
                return []
            }
        },
        macosReleases () {
            try {
                return this.releases.macos
            } catch (e) {
                return []
            }
        },
        windowsReleases () {
            try {
                return this.releases.windows
            } catch (e) {
                return []
            }
        }
    },
    async mounted () {
        const response = await axios({
            method: 'get',
            url: '/static/index/releases.json'
        })

        console.log(response.data)
    }
})