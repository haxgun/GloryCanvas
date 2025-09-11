from app.module.utils.dotaprofile import DotaProfile

if __name__ == '__main__':
    profile = DotaProfile('https://steamcommunity.com/profiles/76561198850706100/')
    profiles = profile.export()
    print(profiles)
