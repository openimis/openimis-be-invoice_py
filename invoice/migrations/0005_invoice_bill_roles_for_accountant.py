import logging

from django.db import migrations

logger = logging.getLogger(__name__)


MIGRATION_SQL = """
    /* Invoice */
    DECLARE @SystemRole INT
    SELECT @SystemRole = role.RoleID from tblRole role where IsSystem=4;
    /* Invoice search */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155101)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155101, CURRENT_TIMESTAMP)
    END
    /* Invoice create */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155102)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155102, CURRENT_TIMESTAMP)
    END
    /* Invoice update */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155103)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155103, CURRENT_TIMESTAMP)
    END
    /* Invoice delete */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155104)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155104, CURRENT_TIMESTAMP)
    END
    /* Invoice amend */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155109)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155109, CURRENT_TIMESTAMP)
    END
    /* Invoice Payment search */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155201)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155201, CURRENT_TIMESTAMP)
    END
    /* Invoice Payment create */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155202)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155202, CURRENT_TIMESTAMP)
    END
    /* Invoice Payment update */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155203)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155203, CURRENT_TIMESTAMP)
    END
    /* Invoice Payment delete */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155204)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155204, CURRENT_TIMESTAMP)
    END
    /* Invoice Payment refund */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155206)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155206, CURRENT_TIMESTAMP)
    END
    /* Invoice Event search */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155301)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155301, CURRENT_TIMESTAMP)
    END
    /* Invoice Event create */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155302)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155302, CURRENT_TIMESTAMP)
    END
    /* Invoice Event update */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155303)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155303, CURRENT_TIMESTAMP)
    END
    /* Invoice Event delete */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155304)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155304, CURRENT_TIMESTAMP)
    END
    /* Invoice Event create message */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155306)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155306, CURRENT_TIMESTAMP)
    END
    /* Invoice Event delete my message */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155307)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155307, CURRENT_TIMESTAMP)
    END
    /* Invoice Event delete all message */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 155308)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 155308, CURRENT_TIMESTAMP)
    END
    /* Bill search */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156101)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156101, CURRENT_TIMESTAMP)
    END
    /* Bill create */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156102)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156102, CURRENT_TIMESTAMP)
    END
    /* Bill update */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156103)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156103, CURRENT_TIMESTAMP)
    END
    /* Bill delete */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156104)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156104, CURRENT_TIMESTAMP)
    END
    /* Bill amend */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156109)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156109, CURRENT_TIMESTAMP)
    END
    /* Bill Payment search */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156201)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156201, CURRENT_TIMESTAMP)
    END
    /* Bill Payment create */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156202)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156202, CURRENT_TIMESTAMP)
    END
    /* Bill Payment update */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156203)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156203, CURRENT_TIMESTAMP)
    END
    /* Bill Payment delete */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156204)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156204, CURRENT_TIMESTAMP)
    END
    /* Bill Payment refund */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156206) 
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156206, CURRENT_TIMESTAMP)
    END
    /* Bill Event search */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156301)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156301, CURRENT_TIMESTAMP)
    END
    /* Bill Event create */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156302)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156302, CURRENT_TIMESTAMP)
    END
    /* Bill Event update */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156303)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156303, CURRENT_TIMESTAMP)
    END
    /* Bill Event delete */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156304)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156304, CURRENT_TIMESTAMP)
    END
    /* Bill Event create message */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156306)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156306, CURRENT_TIMESTAMP)
    END
    /* Bill Event delete my message */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156307)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156307, CURRENT_TIMESTAMP)
    END
    /* Bill Event delete all message */
    IF NOT EXISTS (SELECT * FROM [tblRoleRight] WHERE [RoleID] = @SystemRole AND [RightID] = 156308)
    BEGIN
        INSERT [dbo].[tblRoleRight] ([RoleID], [RightID], [ValidityFrom])
        VALUES (@SystemRole, 156308, CURRENT_TIMESTAMP)
    END
"""


class Migration(migrations.Migration):
    dependencies = [
        ('invoice', '0004_invoice_bill_roles_for_admin')
    ]

    operations = [
        migrations.RunSQL(sql=MIGRATION_SQL),
    ]
